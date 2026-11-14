#!/usr/bin/env python3
"""Tests hors ligne : API Instagram et API GitHub simulées en local, aucun vrai token.

    python3 -m unittest discover -s tests -v      (PyNaCl requis pour le test de rotation)
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FAKE_TOKEN = "IGAAtokenTEST" + "x" * 40


class Mock:
    """État partagé du faux serveur."""
    def reset(self):
        self.calls = []
        self.username = "hexplique"
        self.uploaded = b""
        self.status_seq = ["IN_PROGRESS", "FINISHED"]
        self.secrets = {}
        self.variables = {}
        self.refresh_ok = True
        self.nacl_pk = None
        self.app_pubkey_pem = None


M = Mock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        M.calls.append(("GET", u.path, q))
        if u.path.endswith("/me"):
            return self._send(200, {"user_id": "1784", "username": M.username})
        if u.path == "/ig/refresh_access_token":
            if not M.refresh_ok:
                return self._send(400, {"error": {"message": "bad token"}})
            return self._send(200, {"access_token": "IGAAnewTOKEN" + "y" * 40, "token_type": "bearer",
                                    "expires_in": 5184000})
        if u.path.startswith("/ig/") and u.path.count("/") == 3:  # statut du conteneur
            st = M.status_seq.pop(0) if len(M.status_seq) > 1 else M.status_seq[0]
            return self._send(200, {"status_code": st})
        if u.path == "/gh/repos/o/r/installation":
            self._check_jwt()
            return self._send(200, {"id": 42})
        if u.path == "/gh/repos/o/r/actions/secrets/public-key":
            return self._send(200, {"key_id": "k1", "key": base64.b64encode(bytes(M.nacl_pk)).decode()})
        return self._send(404, {"message": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        raw = self._body()
        M.calls.append(("POST", u.path, raw[:200]))
        if u.path.endswith("/media") and u.path.startswith("/ig/"):
            port = self.server.server_address[1]
            return self._send(200, {"id": "C9", "uri": f"http://127.0.0.1:{port}/rupload/ig-api-upload/v0/C9"})
        if u.path.startswith("/rupload/"):
            assert self.headers["Authorization"].startswith("OAuth ")
            assert int(self.headers["file_size"]) == len(raw)
            M.uploaded = raw
            return self._send(200, {"success": True})
        if u.path.endswith("/media_publish"):
            return self._send(200, {"id": "MEDIA123"})
        if u.path == "/gh/app/installations/42/access_tokens":
            self._check_jwt()
            return self._send(201, {"token": "ghs_installTOKEN" + "z" * 30})
        if u.path == "/gh/repos/o/r/actions/variables":
            d = json.loads(raw)
            M.variables[d["name"]] = d["value"]
            return self._send(201, {})
        return self._send(404, {"message": "not found"})

    def do_PUT(self):
        u = urllib.parse.urlparse(self.path)
        d = json.loads(self._body())
        M.calls.append(("PUT", u.path, None))
        if u.path.startswith("/gh/repos/o/r/actions/secrets/"):
            M.secrets[u.path.rsplit("/", 1)[1]] = d
            return self._send(201, {})
        return self._send(404, {})

    def do_PATCH(self):
        u = urllib.parse.urlparse(self.path)
        self._body()
        M.calls.append(("PATCH", u.path, None))
        return self._send(404, {"message": "Not Found"})  # variable pas encore créée

    def _check_jwt(self):
        jwt = self.headers["Authorization"].split()[1]
        h, p, s = jwt.split(".")
        sig = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
        with tempfile.TemporaryDirectory() as d:
            Path(d, "pub.pem").write_bytes(M.app_pubkey_pem)
            Path(d, "sig").write_bytes(sig)
            r = subprocess.run(["openssl", "dgst", "-sha256", "-verify", f"{d}/pub.pem", "-signature", f"{d}/sig"],
                               input=f"{h}.{p}".encode(), capture_output=True)
        assert r.returncode == 0, "signature JWT invalide"


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.port = cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        M.reset()
        self.tmp = Path(tempfile.mkdtemp())
        self.env = {**os.environ, "IG_GRAPH_BASE": f"http://127.0.0.1:{self.port}/ig",
                    "GITHUB_API": f"http://127.0.0.1:{self.port}/gh", "META_API_VERSION": "v0",
                    "IG_EXPECTED_USERNAME": "hexplique", "POLL_EVERY": "0", "NO_PROXY": "127.0.0.1",
                    "no_proxy": "127.0.0.1"}
        self.env.pop("GITHUB_ACTIONS", None)
        self.env.pop("GITHUB_STEP_SUMMARY", None)
        self.env.pop("GITHUB_OUTPUT", None)

    def run_script(self, name, **extra):
        r = subprocess.run([sys.executable, str(SCRIPTS / name)], env={**self.env, **extra},
                           capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        for secret in (FAKE_TOKEN, "IGAAnewTOKEN", "ghs_installTOKEN", "PRIVATE KEY"):
            self.assertNotIn(secret, out, f"secret affiché par {name}")
        return r.returncode, out


class TestPublish(Base):
    def media(self, episode="A06", tamper=False):
        media = self.tmp / "media"
        media.mkdir()
        video = b"\x00\x00\x00\x18ftypmp42" + os.urandom(4096)
        (media / "reelA06_test.mp4").write_bytes(video)
        digest = hashlib.sha256(video).hexdigest()
        if tamper:
            (media / "reelA06_test.mp4").write_bytes(video + b"!")
        (media / f"{episode}.json").write_text(json.dumps(
            {"episode": episode, "file": "reelA06_test.mp4", "sha256": digest, "caption": "Légende #hexplique"}))
        return media, video

    def publish(self, mode, **kw):
        media, video = self.media(**kw)
        state = self.tmp / "state.json"
        code, out = self.run_script("publish_meta.py", EPISODE="A06", MODE=mode, IG_TOKEN=FAKE_TOKEN,
                                    MEDIA_DIR=str(media), STATE_FILE=str(state))
        return code, out, video, state

    def test_essai_ne_publie_pas(self):
        code, out, video, state = self.publish("essai")
        self.assertEqual(code, 0, out)
        self.assertEqual(M.uploaded, video)
        self.assertFalse(any(c[1].endswith("/media_publish") for c in M.calls))
        self.assertFalse(state.exists())

    def test_publication(self):
        code, out, video, state = self.publish("publier")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(state.read_text())[0]["media_id"], "MEDIA123")
        create = [c for c in M.calls if c[1].endswith("/media") and c[0] == "POST"][0]
        self.assertIn(b"upload_type=resumable", create[2])
        self.assertIn(b"media_type=REELS", create[2])
        self.assertNotIn(b"share_to_feed", create[2])

    def test_empreinte_differente_refusee(self):
        code, out, _, _ = self.publish("publier", tamper=True)
        self.assertNotEqual(code, 0)
        self.assertIn("empreinte", out)
        self.assertEqual(M.calls, [])

    def test_doublon_refuse(self):
        media, _ = self.media()
        state = self.tmp / "state.json"
        state.write_text(json.dumps([{"episode": "A06", "media_id": "X"}]))
        code, out = self.run_script("publish_meta.py", EPISODE="A06", MODE="publier", IG_TOKEN=FAKE_TOKEN,
                                    MEDIA_DIR=str(media), STATE_FILE=str(state))
        self.assertNotEqual(code, 0)
        self.assertIn("déjà publié", out)
        self.assertEqual(M.calls, [])

    def test_mauvais_compte_refuse(self):
        M.reset()
        M.username = "autre_compte"
        media, _ = self.media()
        code, out = self.run_script("publish_meta.py", EPISODE="A06", MODE="publier", IG_TOKEN=FAKE_TOKEN,
                                    MEDIA_DIR=str(media), STATE_FILE=str(self.tmp / "s.json"))
        self.assertNotEqual(code, 0)
        self.assertFalse(any(c[1].endswith("/media") for c in M.calls))

    def test_episode_invalide(self):
        media, _ = self.media()
        code, out = self.run_script("publish_meta.py", EPISODE="A06; rm -rf /", MODE="publier",
                                    IG_TOKEN=FAKE_TOKEN, MEDIA_DIR=str(media), STATE_FILE=str(self.tmp / "s.json"))
        self.assertNotEqual(code, 0)

    def test_erreur_meta(self):
        M.status_seq = ["ERROR"]
        code, out, _, state = self.publish("publier")
        self.assertNotEqual(code, 0)
        self.assertFalse(state.exists())


class TestRotation(Base):
    def setUp(self):
        super().setUp()
        from nacl import public
        self.sk = public.PrivateKey.generate()
        M.nacl_pk = self.sk.public_key
        key = subprocess.run(["openssl", "genrsa", "2048"], capture_output=True, check=True).stdout
        M.app_pubkey_pem = subprocess.run(["openssl", "rsa", "-pubout"], input=key, capture_output=True,
                                          check=True).stdout
        self.app_key = key.decode()

    def rotate(self):
        return self.run_script("rotate_token.py", IG_TOKEN=FAKE_TOKEN, APP_ID="123",
                               APP_PRIVATE_KEY=self.app_key, GITHUB_REPOSITORY="o/r")

    def test_rotation_reecrit_le_secret(self):
        from nacl import public
        code, out = self.rotate()
        self.assertEqual(code, 0, out)
        enc = base64.b64decode(M.secrets["IG_TOKEN"]["encrypted_value"])
        self.assertTrue(public.SealedBox(self.sk).decrypt(enc).decode().startswith("IGAAnewTOKEN"))
        self.assertIn("IG_TOKEN_EXPIRES_AT", M.variables)

    def test_refus_meta_ne_touche_pas_au_secret(self):
        M.refresh_ok = False
        code, out = self.rotate()
        self.assertNotEqual(code, 0)
        self.assertEqual(M.secrets, {})


class TestSante(Base):
    def test_ok(self):
        from datetime import datetime, timedelta, timezone
        exp = (datetime.now(timezone.utc) + timedelta(days=50)).isoformat()
        code, out = self.run_script("health.py", IG_TOKEN=FAKE_TOKEN, IG_TOKEN_EXPIRES_AT=exp)
        self.assertEqual(code, 0, out)

    def test_expiration_proche(self):
        from datetime import datetime, timedelta, timezone
        exp = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        code, out = self.run_script("health.py", IG_TOKEN=FAKE_TOKEN, IG_TOKEN_EXPIRES_AT=exp)
        self.assertNotEqual(code, 0)
        self.assertIn("expire", out)


if __name__ == "__main__":
    unittest.main()
