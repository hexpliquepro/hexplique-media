#!/usr/bin/env python3
"""Publie un réel validé sur Instagram par upload direct chez Meta (aucune URL publique).

Lancé par le workflow « publier » de hexplique-publish, sur clic du propriétaire.
Entrées (variables d'environnement) :
  EPISODE              identifiant de l'épisode (ex. 04, A06)
  MODE                 « essai » (tout sauf la publication) ou « publier »
  IG_TOKEN             secret : token long Instagram (Instagram Login)
  META_API_VERSION     version de l'API Graph (ex. v24.0)
  IG_GRAPH_BASE        hôte de l'API (défaut https://graph.instagram.com ; https://graph.facebook.com
                       avec Facebook Login for Business)
  IG_USER_ID           facultatif avec Instagram Login, obligatoire avec Facebook Login for Business
  IG_EXPECTED_USERNAME garde-fou : nom du compte attendu (ex. hexplique)
  MEDIA_DIR            clone de la branche « content » de hexplique-media
  STATE_FILE           historique des publications (anti-doublon)

Déroulé (API Instagram, upload « resumable ») :
  1. POST /{ig-user-id}/media  media_type=REELS, upload_type=resumable → conteneur + URL d'envoi
     (pas de share_to_feed : non listé pour l'upload resumable ; un réel apparaît dans le fil par défaut)
  2. POST rupload.facebook.com/... (octets du MP4, en-tête Authorization: OAuth <token>)
  3. GET /{conteneur}?fields=status_code jusqu'à FINISHED
  4. POST /{ig-user-id}/media_publish (sauf en mode essai : le conteneur expire seul sous 24 h)
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ApiError, fail, ig_me, ig_url, need_env, register_secret, request,  # noqa: E402
                    sanitize, summary)

EPISODE_RE = re.compile(r"^A?\d{2,3}$")
FILE_RE = re.compile(r"^reel[A-Za-z0-9_\-]+\.mp4$")
MAX_BYTES = 1024 ** 3
POLL_EVERY = int(os.environ.get("POLL_EVERY", "10"))
POLL_MAX = int(os.environ.get("POLL_MAX", "60"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ticket(media_dir, episode):
    p = media_dir / f"{episode}.json"
    if not p.is_file():
        fail(f"ticket introuvable sur la branche content : {episode}.json")
    t = json.loads(p.read_text(encoding="utf-8"))
    for k in ("episode", "file", "sha256", "caption"):
        if not isinstance(t.get(k), str) or not t[k]:
            fail(f"ticket {episode} invalide : champ « {k} » manquant")
    if t["episode"] != episode:
        fail(f"ticket incohérent : épisode {t['episode']} ≠ {episode}")
    if not FILE_RE.match(t["file"]):
        fail(f"nom de fichier refusé : {t['file']!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", t["sha256"]):
        fail("empreinte SHA-256 du ticket invalide")
    if len(t["caption"]) > 2200:
        fail("légende trop longue (> 2200 caractères)")
    return t


def main():
    episode = need_env("EPISODE").upper()
    if not EPISODE_RE.match(episode):
        fail(f"identifiant d'épisode refusé : {episode!r}")
    mode = need_env("MODE")
    if mode not in ("essai", "publier"):
        fail("MODE doit valoir « essai » ou « publier »")
    token = need_env("IG_TOKEN")
    register_secret(token)
    version = need_env("META_API_VERSION")
    expected = need_env("IG_EXPECTED_USERNAME")
    media_dir = Path(need_env("MEDIA_DIR")).resolve()
    state_file = Path(need_env("STATE_FILE"))

    ticket = load_ticket(media_dir, episode)
    video = (media_dir / ticket["file"]).resolve()
    if video.parent != media_dir or not video.is_file():
        fail(f"vidéo introuvable : {ticket['file']}")
    size = video.stat().st_size
    if not 0 < size <= MAX_BYTES:
        fail(f"taille de vidéo invalide : {size} octets")
    digest = sha256(video)
    if digest != ticket["sha256"]:
        fail(f"empreinte différente de la version validée ({digest[:12]}… ≠ {ticket['sha256'][:12]}…)")

    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.is_file() else []
    if any(e.get("episode") == episode for e in state):
        fail(f"l'épisode {episode} est déjà publié : publication refusée")

    try:
        me = ig_me(token, version)
        if me.get("username") != expected:
            fail(f"le token désigne le compte « {me.get('username')} », attendu « {expected} »")
        user_id = me["user_id"]

        cont = request("POST", ig_url(version, f"{user_id}/media"), data={
            "media_type": "REELS", "upload_type": "resumable", "caption": ticket["caption"],
            "access_token": token})
        cid = cont["id"]
        upload_uri = cont.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{version}/{cid}"
        print(f"conteneur créé : {cid}")

        with open(video, "rb") as f:
            res = request("POST", upload_uri, raw=f.read(), timeout=600, headers={
                "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
        if res.get("success") is False:
            fail(f"envoi refusé par Meta : {res}")
        print(f"vidéo envoyée ({size} octets)")

        status = None
        for _ in range(POLL_MAX):
            st = request("GET", ig_url(version, cid),
                         params={"fields": "status_code,status", "access_token": token})
            status = st.get("status_code")
            if status == "FINISHED":
                break
            if status in ("ERROR", "EXPIRED"):
                fail(f"traitement Meta en échec : {status} ({st.get('status')})")
            time.sleep(POLL_EVERY)
        if status != "FINISHED":
            fail(f"traitement Meta trop long (dernier statut : {status})")
        print("traitement Meta terminé")

        if mode == "essai":
            summary(f"### Essai réussi — {episode}\n\nVidéo vérifiée (SHA-256 `{digest[:12]}…`), envoyée et "
                    f"traitée par Meta. **Rien n'a été publié** : le conteneur `{cid}` expirera seul.")
            return

        pub = request("POST", ig_url(version, f"{user_id}/media_publish"),
                      data={"creation_id": cid, "access_token": token})
        media_id = pub["id"]
    except ApiError as e:
        fail(f"API Meta : {e}")
    except KeyError as e:
        fail(f"réponse Meta inattendue (champ {e} absent)")

    state.append({"episode": episode, "sha256": digest, "media_id": media_id,
                  "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"media_id={media_id}\n")
    summary(f"### Publié — {episode}\n\nRéel Instagram publié : media `{media_id}`.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # jamais de trace brute : elle pourrait contenir un secret
        fail(f"erreur inattendue : {type(e).__name__} : {sanitize(e)}")
