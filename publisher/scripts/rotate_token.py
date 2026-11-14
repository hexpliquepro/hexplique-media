#!/usr/bin/env python3
"""Renouvelle le token Instagram (60 jours) et réécrit le secret GitHub IG_TOKEN.

Lancé chaque semaine par le workflow « rotation-token ». Entrées :
  IG_TOKEN            secret : token actuel
  APP_ID              variable : identifiant de la GitHub App « hexplique-rotation »
  APP_PRIVATE_KEY     secret : clé privée de cette App
  GITHUB_REPOSITORY   dépôt cible (fourni par GitHub Actions)
  META_API_VERSION    version de l'API Graph (vérification du nouveau token)

Ordre choisi pour ne jamais perdre de token : on prépare d'abord l'accès GitHub et la clé de
chiffrement, puis on renouvelle, puis on écrit le secret (avec réessais), puis on vérifie.
"""
import base64
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ApiError, IG_GRAPH_BASE, fail, gh, ig_me, need_env, register_secret, request, summary  # noqa: E402
from github_app import installation_token  # noqa: E402

VAR_EXPIRES = "IG_TOKEN_EXPIRES_AT"


def encrypt(public_key_b64, value):
    from nacl import encoding, public  # PyNaCl, version épinglée dans requirements.txt
    box = public.SealedBox(public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder()))
    return base64.b64encode(box.encrypt(value.encode())).decode()


def set_variable(repo, token, name, value):
    try:
        gh("PATCH", f"repos/{repo}/actions/variables/{name}", token, json_body={"name": name, "value": value})
    except ApiError as e:
        if e.status != 404:
            raise
        gh("POST", f"repos/{repo}/actions/variables", token, json_body={"name": name, "value": value})


def main():
    if os.environ.get("ROTATION_ENABLED", "true").strip().lower() == "false":
        summary("### Rotation désactivée\n\nToken sans expiration (utilisateur système) : rien à faire.")
        return
    old = need_env("IG_TOKEN")
    register_secret(old)
    app_id = need_env("APP_ID")
    key = need_env("APP_PRIVATE_KEY")
    register_secret(key)
    repo = need_env("GITHUB_REPOSITORY")
    version = need_env("META_API_VERSION")

    try:
        gh_token = installation_token(app_id, key, repo)
        pk = gh("GET", f"repos/{repo}/actions/secrets/public-key", gh_token)
    except ApiError as e:
        fail(f"accès GitHub App impossible (rien n'a été renouvelé) : {e}")

    try:
        res = request("GET", f"{IG_GRAPH_BASE}/refresh_access_token",
                      params={"grant_type": "ig_refresh_token", "access_token": old})
        new, expires_in = res["access_token"], int(res["expires_in"])
    except (ApiError, KeyError, ValueError) as e:
        fail(f"renouvellement refusé par Meta (l'ancien token reste en place) : {e}")
    register_secret(new)

    try:
        gh("PUT", f"repos/{repo}/actions/secrets/IG_TOKEN", gh_token, retries=5,
           json_body={"encrypted_value": encrypt(pk["key"], new), "key_id": pk["key_id"]})
    except ApiError as e:
        fail(f"CRITIQUE : nouveau token obtenu mais non enregistré ({e}). Régénérer un token à la main.")

    expires_at = (datetime.datetime.now(datetime.timezone.utc)
                  + datetime.timedelta(seconds=expires_in)).isoformat(timespec="seconds")
    try:
        set_variable(repo, gh_token, VAR_EXPIRES, expires_at)
    except ApiError as e:
        print(f"avertissement : date d'expiration non enregistrée ({e})")

    try:
        ig_me(new, version)
    except ApiError as e:
        fail(f"le nouveau token ne répond pas : {e}")
    summary(f"### Token Instagram renouvelé\n\nNouvelle expiration : `{expires_at}`.")


if __name__ == "__main__":
    main()
