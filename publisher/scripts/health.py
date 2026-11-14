#!/usr/bin/env python3
"""Vérification quotidienne : token Instagram valide, bon compte, expiration lointaine.

Entrées : IG_TOKEN (secret), META_API_VERSION, IG_EXPECTED_USERNAME, IG_TOKEN_EXPIRES_AT (variable,
tenue à jour par la rotation). Échoue (→ issue d'alerte + mail GitHub) si un contrôle ne passe pas.
"""
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ApiError, fail, ig_me, need_env, register_secret, summary  # noqa: E402

WARN_DAYS = 14


def main():
    token = need_env("IG_TOKEN")
    register_secret(token)
    version = need_env("META_API_VERSION")
    expected = need_env("IG_EXPECTED_USERNAME")
    problems = []

    try:
        me = ig_me(token, version)
        if me.get("username") != expected:
            problems.append(f"le token désigne « {me.get('username')} » au lieu de « {expected} »")
    except ApiError as e:
        problems.append(f"token Instagram refusé : {e}")

    exp = os.environ.get("IG_TOKEN_EXPIRES_AT", "").strip()
    if os.environ.get("ROTATION_ENABLED", "true").strip().lower() == "false":
        exp = exp or "sans objet (token sans expiration)"
    elif not exp:
        problems.append("date d'expiration inconnue (aucune rotation réussie enregistrée)")
    else:
        left = (datetime.datetime.fromisoformat(exp) - datetime.datetime.now(datetime.timezone.utc)).days
        if left < WARN_DAYS:
            problems.append(f"le token expire dans {left} jour(s) : la rotation automatique ne fonctionne plus")

    if problems:
        fail(" ; ".join(problems))
    summary("### Santé : OK\n\nToken Instagram valide, compte attendu, expiration le " + exp + ".")


if __name__ == "__main__":
    main()
