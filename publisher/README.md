# hexplique-publish

Publication des réels @hexplique **par upload direct chez Meta**, sans aucune URL publique.
Ce dépôt est **privé**, appartient au compte GitHub **personnel** du propriétaire, et l'agent IA
(compte `hexpliquepro`) n'y a **aucun accès**. Les secrets Meta ne vivent qu'ici.

> Source du code : `hexpliquepro/hexplique-media`, dossier `publisher/`. Les mises à jour arrivent
> par une PR du workflow « synchronisation », à relire avant fusion.

## Fonctionnement

```
hexplique-media (privé, agent)                 hexplique-publish (privé, propriétaire)
  branche content : <EP>.json + reel….mp4  ──►  publier (clic du propriétaire)
  (lecture seule, clé de déploiement)              vérifie SHA-256, anti-doublon, bon compte
                                                   upload direct chez Meta → réel publié
                                                rotation-token (lundi)  : renouvelle IG_TOKEN
                                                sante (chaque jour)      : token, expiration, clé
                                                rappels (janv. / juil.)  : clés à tourner à la main
                                                synchronisation (lundi)  : PR des mises à jour
```

Aucune action GitHub tierce : uniquement git, ssh et Python (bibliothèque standard ; PyNaCl épinglé
par empreinte pour la rotation). Les alertes ouvrent une issue ici : GitHub envoie un mail.

## Publier un réel

1. L'agent prévient (notification) : « A06 prêt ».
2. Ici : **Actions → publier → Run workflow**, épisode `A06`, mode **publier** (ou **essai** pour tout
   faire sauf la mise en ligne).
3. Le résumé du run donne l'identifiant du réel. L'agent met le calendrier à jour.

## Installation (une seule fois, ~45 min)

### 1. Dépôt
- Créer le dépôt **privé** `hexplique-publish` sur le compte personnel.
- Y déposer le contenu du dossier `publisher/` (Add file → Upload files), y compris `.github/workflows`.
- Settings → Actions → General → Workflow permissions : **Read and write**, et cocher
  « Allow GitHub Actions to create and approve pull requests » (pour la synchronisation).

### 2. Clé de déploiement (lecture seule sur hexplique-media)
- Sur un poste de confiance : `ssh-keygen -t ed25519 -C hexplique-publish -f deploy_hexplique -N ""`.
- Sur **hexplique-media** (compte hexpliquepro) : Settings → Deploy keys → Add : coller
  `deploy_hexplique.pub`, **ne pas** cocher « Allow write access ».
- Sur **hexplique-publish** : secret `MEDIA_DEPLOY_KEY` = contenu de `deploy_hexplique` (clé privée).
- Supprimer les deux fichiers du poste.

### 3. App Meta et token Instagram
- developers.facebook.com → créer une app (type Business) → produit **Instagram** → « API setup with
  Instagram login ».
- Ajouter le compte @hexplique, permissions `instagram_business_basic` et
  `instagram_business_content_publish`, générer le **token long** (60 jours).
- Secret `IG_TOKEN` = ce token. Ne jamais le coller ailleurs (chat, fichier, mail).
- Variables : `META_API_VERSION` (version affichée dans le tableau de bord, ex. `v24.0`),
  `IG_EXPECTED_USERNAME` = `hexplique`, `MEDIA_REPO` = `hexpliquepro/hexplique-media`.

> ⚠️ Point à valider par l'essai : la documentation Meta de l'upload « resumable » mentionne
> Facebook Login for Business. Si l'essai échoue avec un token Instagram Login, basculer sur
> Facebook Login for Business : variables `IG_GRAPH_BASE` = `https://graph.facebook.com` et
> `IG_USER_ID` = identifiant du compte Instagram ; avec un token d'utilisateur système (sans
> expiration), `ROTATION_ENABLED` = `false`. Le code gère les deux cas.

### 4. GitHub App « hexplique-rotation » (renouvellement automatique du token)
- Settings (compte personnel) → Developer settings → GitHub Apps → New : nom `hexplique-rotation`,
  sans webhook, **Only on this account**.
- Permissions du dépôt : **Secrets : Read and write**, **Variables : Read and write**,
  **Issues : Read and write**. Rien d'autre.
- Installer l'App sur **hexplique-publish uniquement**.
- Générer une clé privée : secret `APP_PRIVATE_KEY` = contenu complet du `.pem`, puis supprimer le fichier.
- Variable `APP_ID` = identifiant numérique de l'App.

### 5. Vérifications
- Lancer **rotation-token** à la main (le token doit avoir au moins 24 h) → variable
  `IG_TOKEN_EXPIRES_AT` créée.
- Lancer **sante** → vert.
- Lancer **publier** en mode **essai** sur un épisode présent sur la branche `content`.

## Rotation manuelle (rappel semestriel)

GitHub ne permet pas de générer par API une clé de GitHub App ni une clé de déploiement.
- **Clé de l'App** : App → Generate a private key → remplacer `APP_PRIVATE_KEY` → lancer
  rotation-token → supprimer l'ancienne clé dans l'App.
- **Clé de déploiement** : nouvelle paire (§ 2) → l'ajouter sur hexplique-media → remplacer
  `MEDIA_DEPLOY_KEY` → lancer sante → supprimer l'ancienne clé de déploiement.

## Sécurité

- Zéro secret dans le code : tout passe par les secrets du dépôt ; voir `.env.example` (sans valeurs).
- Jetons masqués dans les journaux et dans les messages d'erreur.
- Entrées des workflows passées par variables d'environnement (pas d'injection de commande).
- Garde-fous : empreinte SHA-256 de la vidéo validée, nom du compte attendu, anti-doublon.
- Tests hors ligne : `python3 -m unittest discover -s tests` (APIs simulées, aucun vrai token).
