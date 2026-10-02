#!/usr/bin/env python3
"""Build locally on the rover; keep signing material private for updates."""
from pathlib import Path
import os
import secrets
import subprocess
import zipfile

root = Path(__file__).resolve().parent
os.chdir(root)
os.umask(0o077)
build = root / "build"
build.mkdir(exist_ok=True)
signing = root / "signing"
signing.mkdir(mode=0o700, exist_ok=True)
password = signing / "password"
keystore = signing / "rover-usb-link.jks"
if not password.exists():
    password.write_text(secrets.token_urlsafe(32) + "\n")
    password.chmod(0o600)

def run(*args):
    subprocess.run(list(map(str, args)), check=True)

run("smali", "assemble", "--api", "19", "smali", "-o", build / "classes.dex")
run("aapt", "package", "-f", "-M", "AndroidManifest.xml", "-I",
    "/home/rover/modem-framework-res.apk", "-F", build / "unsigned.apk")
with zipfile.ZipFile(build / "unsigned.apk", "a", zipfile.ZIP_DEFLATED) as apk:
    apk.write(build / "classes.dex", "classes.dex")
if not keystore.exists():
    run("keytool", "-genkeypair", "-keystore", keystore, "-storetype", "JKS",
        "-storepass:file", password, "-keypass:file", password,
        "-alias", "rover-usb-link", "-keyalg", "RSA", "-keysize", "2048",
        "-validity", "3650", "-dname", "CN=Rover USB Link")
run("apksigner", "sign", "--ks", keystore, "--ks-key-alias", "rover-usb-link",
    "--ks-pass", "file:" + str(password),
    "--min-sdk-version", "19", "--v1-signing-enabled", "true",
    "--out", build / "rover-usb-link.apk", build / "unsigned.apk")
run("apksigner", "verify", "--min-sdk-version", "19", "--verbose",
    build / "rover-usb-link.apk")
run("aapt", "dump", "permissions", build / "rover-usb-link.apk")
print("Built and verified:", build / "rover-usb-link.apk", flush=True)
