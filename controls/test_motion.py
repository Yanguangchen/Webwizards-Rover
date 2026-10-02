import unittest
from motion import MotionGuard, MotionError


class MotionTest(unittest.TestCase):
    def setUp(self):
        self.now = 10.0
        self.sent = []
        self.guard = MotionGuard(self.sent.append, clock=lambda:self.now, enabled=True)
        self.guard.ready = True
        self.sid = self.guard.session()['session']

    def request(self, action, seq, **data):
        return self.guard.request(action, {'session':self.sid,'sequence':seq,**data})

    def prepare(self):
        return self.request('prepare',1)['token']

    def drive(self, token, seq=2):
        return self.request('drive',seq,token=token,L=0.1,R=0.1)

    def test_stop_before_delayed_prepare_cannot_start(self):
        self.request('stop',2)
        with self.assertRaises(MotionError): self.prepare()
        self.guard.tick()
        self.assertEqual(self.sent[-1], {'T':1,'L':0,'R':0})

    def test_stop_before_delayed_drive_cannot_restart(self):
        token = self.prepare()
        self.request('stop',3)
        with self.assertRaises(MotionError): self.drive(token)
        self.guard.tick()
        self.assertTrue(all(command['L']==command['R']==0 for command in self.sent))

    def test_lost_release_stops_on_robot_deadline(self):
        token = self.prepare()
        self.drive(token)
        self.guard.tick()
        self.assertEqual(self.sent[-1]['L'],0.1)
        self.now += 0.501
        self.guard.tick()
        self.assertEqual(self.sent[-1], {'T':1,'L':0,'R':0})

    def test_late_packet_does_not_get_a_fresh_full_lease(self):
        token = self.prepare()
        self.now += 0.49
        self.drive(token)
        self.now += 0.02
        self.guard.tick()
        self.assertEqual(self.sent[-1]['L'],0)

    def test_expired_renewal_token_cannot_resurrect_motion(self):
        token = self.drive(self.prepare())['token']
        self.now += 0.6
        with self.assertRaises(MotionError): self.drive(token,3)
        self.guard.tick()
        self.assertEqual(self.sent[-1]['L'],0)

    def test_old_token_cannot_be_replayed(self):
        token = self.prepare()
        self.drive(token)
        with self.assertRaises(MotionError): self.drive(token,3)
        self.guard.tick()
        self.assertEqual(self.sent[-1]['L'],0)

    def test_newer_stop_cancels_pending_renewal(self):
        token = self.drive(self.prepare())['token']
        self.request('stop',4)
        with self.assertRaises(MotionError): self.drive(token,3)
        self.guard.tick()
        self.assertEqual(self.sent[-1]['L'],0)

    def test_speed_cap_and_nonfinite_values_fail_closed(self):
        for speed in (0.251, -0.251, 0.5, -0.5, float('nan'), float('inf'), True):
            with self.subTest(speed=speed):
                self.setUp()
                token = self.prepare()
                with self.assertRaises(MotionError): self.request('drive',2,token=token,L=speed,R=0)
                self.guard.tick()
                self.assertEqual(self.sent[-1]['L'],0)

    def test_increased_maximum_speed_still_expires_on_signal_loss(self):
        token = self.prepare()
        self.request('drive',2,token=token,L=0.25,R=-0.25)
        self.guard.tick()
        self.assertEqual(self.sent[-1], {'T':1,'L':0.25,'R':-0.25})
        self.now += 0.501
        self.guard.tick()
        self.assertEqual(self.sent[-1], {'T':1,'L':0,'R':0})

    def test_other_page_cannot_take_over_active_drive(self):
        self.drive(self.prepare())
        other = self.guard.session()['session']
        with self.assertRaises(MotionError):
            self.guard.request('prepare',{'session':other,'sequence':1})

    def test_controller_error_clears_intent_and_prevents_resume(self):
        token = self.drive(self.prepare())['token']
        def fail(command): raise OSError('simulated controller loss')
        self.guard.send = fail
        self.guard.tick()
        self.assertFalse(self.guard.ready)
        self.assertIsNone(self.guard.intent)
        with self.assertRaises(MotionError): self.drive(token,3)

    def test_failed_prepare_does_not_reserve_controller_forever(self):
        self.prepare()
        self.now += 0.6
        self.guard.tick()
        other = self.guard.session()['session']
        result = self.guard.request('prepare',{'session':other,'sequence':1})
        self.assertIn('token', result)


if __name__ == '__main__': unittest.main()
