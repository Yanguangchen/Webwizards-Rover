import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from relay import RelayServer


class Upstream(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, *_):
        pass

    def do_GET(self):
        self.requests.append(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'<html><head><title>UGV01_BASE_WEB</title></head><body><script>\n    ledCtrl(0);\n</script></body></html>' if self.path == '/' else b'{"v":12.0}')


class RelayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = "test-only-control-key-not-a-real-credential"
        cls.upstream = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        cls.relay = RelayServer(("127.0.0.1", 0), "http://127.0.0.1:" + str(cls.upstream.server_port), cls.key)
        for server in (cls.upstream, cls.relay):
            Thread(target=server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:" + str(cls.relay.server_port)

    @classmethod
    def tearDownClass(cls):
        for server in (cls.relay, cls.upstream):
            server.shutdown()
            server.server_close()

    def get(self, path, key=None):
        return urlopen(Request(self.base + path, headers={"X-Rover-Key": key} if key else {}))

    def test_public_landing_has_no_controller_or_key(self):
        before = len(Upstream.requests)
        body = self.get('/').read()
        self.assertIn(b'Rover controls', body)
        self.assertNotIn(self.key.encode(), body)
        self.assertEqual(len(Upstream.requests), before)

    def test_unauthorized_requests_never_reach_controller(self):
        before = len(Upstream.requests)
        for path in ('/origin/', '/origin/js?' + urlencode({'json':'{"T":1,"L":1,"R":1}'})):
            for key in (None, 'wrong-key'):
                with self.assertRaises(HTTPError) as context:
                    self.get(path, key)
                self.assertEqual(context.exception.code, 401)
        self.assertEqual(len(Upstream.requests), before)

    def test_authorized_ui_is_embeddable_and_authenticates_its_api(self):
        before = len(Upstream.requests)
        response = self.get('/origin/', self.key)
        body = response.read()
        self.assertIn(b'Rover driving controls', body)
        self.assertIn(b"'/origin/js?'", body)
        self.assertIn(b"'X-Rover-Key':key", body)
        for stock_feature in (b'UGV01_BASE_WEB', b'gimbalCtrl', b'jsonSend', b'ledCtrl', b'heartBeat'):
            self.assertNotIn(stock_feature, body)
        self.assertIn(b'"maxSpeed": 0.25', body)
        self.assertEqual(len(Upstream.requests), before)
        self.assertNotIn(b'ledCtrl(0);', body)
        self.assertIn('https://stampnote-omega.vercel.app', response.headers['Content-Security-Policy'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_authenticated_telemetry_preserves_commands(self):
        for command in ({'T':130}, {'T':405}):
            query = urlencode({'json':json.dumps(command)})
            self.assertEqual(self.get('/origin/js?' + query, self.key).status, 200)
            self.assertEqual(Upstream.requests[-1], '/js?' + urlencode({'json':json.dumps(command,separators=(',',':'))}))

    def test_legacy_motion_and_watchdog_bypass_are_rejected(self):
        before = len(Upstream.requests)
        for command in ({'T':1,'L':0.2,'R':0.2}, {'T':11,'L':100,'R':100}, {'T':13,'X':1,'Z':0}, {'T':136,'cmd':0}):
            with self.assertRaises(HTTPError) as context:
                self.get('/origin/js?' + urlencode({'json':json.dumps(command)}), self.key)
            self.assertEqual(context.exception.code, 409)
        self.assertEqual(len(Upstream.requests), before)

    def test_motion_api_requires_auth_and_is_disabled_by_default(self):
        def post(action, data, key=None):
            return urlopen(Request(self.base+'/motion/'+action, data=json.dumps(data).encode(), headers={'X-Rover-Key':key} if key else {}))
        for action in ('session', 'prepare', 'drive', 'stop'):
            with self.assertRaises(HTTPError) as context:
                post(action, {})
            self.assertEqual(context.exception.code, 401)
        sid = json.load(post('session', {}, self.key))['session']
        with self.assertRaises(HTTPError) as context:
            post('prepare', {'session':sid,'sequence':1}, self.key)
        self.assertEqual(context.exception.code, 503)
        self.assertEqual(json.load(post('stop', {'session':sid,'sequence':2}, self.key)), {'stopped':True})

    def test_arbitrary_paths_and_malformed_commands_are_not_forwarded(self):
        before = len(Upstream.requests)
        for path in ('/js?json={}', '/origin/http://example.com/', '/origin/js?json=[]', '/origin/js?json={}', '/origin/js?json={}&json={}'):
            with self.assertRaises(HTTPError) as context:
                self.get(path, self.key)
            self.assertIn(context.exception.code, (400,404))
        self.assertEqual(len(Upstream.requests), before)


if __name__ == '__main__':
    unittest.main()
