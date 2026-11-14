#!/usr/bin/env python3
"""Ouvre (ou complète) une issue d'alerte dans hexplique-publish. GitHub envoie le mail.

Entrées : GITHUB_TOKEN, GITHUB_REPOSITORY, ALERT_TITLE, ALERT_BODY (+ lien vers le run).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import need_env, open_issue  # noqa: E402

repo = need_env("GITHUB_REPOSITORY")
run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
body = os.environ.get("ALERT_BODY", "") + f"\n\nRun : {run}"
open_issue(repo, need_env("GITHUB_TOKEN"), need_env("ALERT_TITLE"), body,
           label=os.environ.get("ALERT_LABEL", "alerte"))
