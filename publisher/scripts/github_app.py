"""Jeton d'installation de la GitHub App « hexplique-rotation » (valable 1 h).

La clé privée de l'App arrive par variable d'environnement (secret GitHub) et n'est jamais
écrite sur disque : elle est passée à openssl par un tube anonyme.
"""
import base64
import json
import os
import subprocess
import time

from common import gh, register_secret


def _b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def app_jwt(app_id, private_key_pem):
    now = int(time.time())
    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": str(app_id)}).encode())
    signing_input = f"{header}.{payload}".encode()
    r, w = os.pipe()
    os.write(w, private_key_pem.encode())
    os.close(w)
    try:
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", f"/dev/fd/{r}"],
                             input=signing_input, capture_output=True, check=True, pass_fds=(r,)).stdout
    finally:
        os.close(r)
    return f"{header}.{payload}.{_b64url(sig)}"


def installation_token(app_id, private_key_pem, repo):
    jwt = app_jwt(app_id, private_key_pem)
    register_secret(jwt)
    inst = gh("GET", f"repos/{repo}/installation", jwt)
    res = gh("POST", f"app/installations/{inst['id']}/access_tokens", jwt,
             json_body={"repositories": [repo.split("/", 1)[1]]})
    token = res["token"]
    register_secret(token)
    return token
