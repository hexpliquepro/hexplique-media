"""Outils communs aux scripts de publication hexplique (bibliothèque standard uniquement).

Politique zéro-secret : aucun secret n'est écrit sur disque ni affiché. Les jetons arrivent
par variables d'environnement (secrets GitHub) et sont masqués dans tout message d'erreur.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IG_GRAPH_BASE = os.environ.get("IG_GRAPH_BASE", "").strip() or "https://graph.instagram.com"
GITHUB_API = os.environ.get("GITHUB_API", "https://api.github.com")

_SECRETS = []


def register_secret(value):
    """Déclare une valeur à masquer partout (logs GitHub Actions compris)."""
    if value:
        _SECRETS.append(value)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::add-mask::{value}")


def sanitize(text):
    text = str(text)
    for s in _SECRETS:
        text = text.replace(s, "***")
    text = re.sub(r"(access_token=)[^&\s\"']+", r"\1***", text)
    text = re.sub(r"((?:OAuth|Bearer|token)\s+)[A-Za-z0-9._\-]{12,}", r"\1***", text)
    return text


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(sanitize(f"HTTP {status} : {body[:500]}"))
        self.status = status


def need_env(name):
    v = os.environ.get(name, "").strip()
    if not v:
        fail(f"variable d'environnement manquante : {name}")
    return v


def fail(msg, code=1):
    print(f"::error::{sanitize(msg)}" if os.environ.get("GITHUB_ACTIONS") == "true"
          else f"ERREUR : {sanitize(msg)}", file=sys.stderr)
    sys.exit(code)


def summary(md):
    """Ajoute du Markdown au résumé du job GitHub Actions (ou l'affiche en local)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(md + "\n")
    print(sanitize(md))


def request(method, url, *, params=None, data=None, json_body=None, headers=None,
            raw=None, timeout=60, retries=3):
    """Requête HTTP(S) ; renvoie le JSON décodé (ou {} si vide). Réessaie sur 429/5xx."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = None
    hdrs = {"User-Agent": "hexplique-publish/1.0"}
    if headers:
        hdrs.update(headers)
    if json_body is not None:
        body = json.dumps(json_body).encode()
        hdrs["Content-Type"] = "application/json"
    elif data is not None:
        body = urllib.parse.urlencode(data).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    elif raw is not None:
        body = raw
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "replace")
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(5 * attempt)
                continue
            raise ApiError(e.code, txt) from None
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(5 * attempt)
                continue
            raise ApiError(0, str(e.reason)) from None


def ig_url(version, path):
    return f"{IG_GRAPH_BASE}/{version}/{path.lstrip('/')}"


def ig_me(token, version):
    """Identité du compte Instagram visé : {"user_id", "username"}.

    IG_USER_ID défini (obligatoire avec Facebook Login for Business) : lecture directe du compte.
    Sinon (Instagram Login) : /me renvoie le compte lié au token.
    """
    uid = os.environ.get("IG_USER_ID", "").strip()
    if uid:
        res = request("GET", ig_url(version, uid), params={"fields": "username", "access_token": token})
        return {"user_id": uid, "username": res.get("username")}
    return request("GET", ig_url(version, "me"),
                   params={"fields": "user_id,username", "access_token": token})


def gh(method, path, token, **kw):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    return request(method, f"{GITHUB_API}/{path.lstrip('/')}", headers=headers, **kw)


def open_issue(repo, token, title, body, label="alerte"):
    """Ouvre une issue d'alerte, ou commente celle déjà ouverte avec le même titre."""
    existing = gh("GET", f"repos/{repo}/issues", token, params={"state": "open", "per_page": 100})
    for it in existing:
        if it.get("title") == title and "pull_request" not in it:
            gh("POST", f"repos/{repo}/issues/{it['number']}/comments", token,
               json_body={"body": sanitize(body)})
            return it["number"]
    try:
        res = gh("POST", f"repos/{repo}/issues", token,
                 json_body={"title": title, "body": sanitize(body), "labels": [label]})
    except ApiError:  # étiquette absente ou refusée : on crée l'issue sans étiquette
        res = gh("POST", f"repos/{repo}/issues", token, json_body={"title": title, "body": sanitize(body)})
    return res.get("number")
