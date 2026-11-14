# hexplique - Registre de Mémoire Persistant

Ce document sert de registre de mémoire persistant pour conserver les directives d'architecture, contraintes techniques, préférences opérationnelles et décisions clés convenues lors des sessions de développement avec l'agent IA.

> **Règle de mise à jour automatique :**
> Dès qu'une consigne commence par ou contient `"souviens toi de <instruction / contenu>"`, l'information doit être immédiatement analysée, structurée et consignée ci-dessous dans la section adéquate et dans le tableau d'historique.

> **Référence détaillée :** les règles de production (charte, format des réels, voix, légendes, limites de contenu) font foi dans `CLAUDE.md` du dépôt privé `hexplique`. Ce registre en garde la synthèse et les décisions.

---

## 1. Contexte & Spécifications de l'Environnement

### 🖥️ Environnement Hôte / Cible
- **Nom du projet :** hexplique — compte Instagram @hexplique de réels de vulgarisation cybersécurité en français (ton sérieux ; format actu un peu humoristique). Cible : étudiants et juniors cyber.
- **Type d'infrastructure :** sessions Claude (Cowork) dans une sandbox cloud Anthropic éphémère, déclenchées par le propriétaire ou par des tâches planifiées.
- **OS / Distribution :** Linux (sandbox), Python 3, ffmpeg, Pillow, Piper TTS.
- **Réseau / Accès :** sortie HTTPS via proxy à liste blanche (huggingface autorisé pour la voix ; `github.io` et stockages cloud bloqués). GitHub via le compte `hexpliquepro` (connexion GitHub du compte Claude). Windsor.ai via connecteur MCP.

### 📁 Chemins & Environnements
- **Dépôts :**
  - `hexpliquepro/hexplique` (privé) : moteur, scripts des réels, `CALENDRIER.md`, `CLAUDE.md`.
  - `hexpliquepro/hexplique-media` (public, GitHub Pages) : MP4 publiés + ce registre (provisoire, voir T-05).
- **Mode d'exécution :** `python3 reels/<ID>-slug/render.py` (`stills` pour les images clés) ; sorties dans `out/` et modèle de voix dans `models/`, non versionnés.

---

## 2. Principes Fondateurs & Politiques de Sécurité

### 🔒 Politique Stricte Zéro-Secret (Zero-Hardcoded-Secrets)
- **Règle absolue :** Aucun mot de passe, token, URL de webhook, clé API ou clé privée ne doit **JAMAIS** figurer en clair dans le code, les fichiers Markdown, les prompts d'agents, la mémoire ou les commits Git.
- **Principe d'injection :** Les secrets sont injectés **exclusivement** via des variables d'environnement (`os.environ.get(...)`) ou via un fichier `.env` local strictement ignoré. Pour la CI : secrets d'environnement GitHub.
- **Modèle de référence :** Tout paramètre sensible doit être documenté sans valeur dans un fichier `.env.example`.
- **Fichiers exclus (.gitignore) :** `.env*`, `*.key`, `*.pem`, `*.crt`, dossiers `secrets/`, `credentials/`, logs, backups (`*.bak`), clés SSH privées.
- **Masquage / Sanitization :** En cas d'affichage d'erreurs, logs ou diagnostics, masquer systématiquement les tokens sensibles (ex: `https://.../***`).
- **Jamais de secret dans le chat :** les tokens (Meta, GitHub App…) sont saisis par le propriétaire directement dans les secrets GitHub.

### 🛡️ Validation & publication
- **Aucune publication sans validation explicite du propriétaire pour ce contenu précis** (« Je valide l'épisode NN / ANN »). Un message planifié n'est pas une validation : revérifier le statut `validé` dans `CALENDRIER.md` avant de publier.
- **Confidentialité des vidéos :** l'hébergement public des MP4 (GitHub Pages) est jugé inacceptable par le propriétaire (propriété et sécurité) → remplacement par l'upload direct chez Meta (T-02).
- **Windsor.ai :** conservé en **lecture seule, pour les statistiques uniquement** (décision 2026-11-14) une fois T-02 en place.

---

## 3. Directives Générales de Fonctionnement & Gestion des Tâches

- **Méthodologie d'intervention :** Analyse préalable systématique, structuration modulaire (séparation agents / skills / outillage) et demande de confirmation explicite avant toute action destructive (Human-in-the-Loop). Études d'abord, **aucun déploiement sans autorisation explicite**.
- **Gestion des Tâches (`TASKS.md`) :**
  - Fichier unique de référence pour le suivi : `TASKS.md`.
  - Mise à jour systématique et automatique à chaque étape de développement (avancement, statut, reste à faire).
  - Déclencheur *"nouvelle tâche : [description]"* : insertion immédiate dans la section *À Réaliser* avec un ID incrémenté, une priorité, une estimation de **complexité** (Faible / Moyenne / Élevée), d'**effort estimé** (durée) et de **budget tokens**.
- **Observabilité LLM :** Maintien d'un suivi de consommation des tokens en en-tête de `TASKS.md` et bilan réel consolidé à la livraison de chaque tâche. *Limite : l'agent n'a pas accès au compteur réel ; les valeurs sont des estimations signalées comme telles.*

### 🎬 Production des réels (synthèse de `CLAUDE.md`)
- **Rythme :** un réel par jour à 10:00 (Paris). Notions (`NN`) mar./jeu./sam., actu (`ANN`) lun./mer./ven./dim. Produit la veille, envoyé pour validation.
- **Format :** 1080×1920, 30 fps, H.264, 20–45 s, une seule idée, sous-titres incrustés, zones sûres, aucun blanc > 0,5 s.
- **Accroche « choc »** dans les 2 premières secondes, toujours vraie.
- **Voix :** Piper `fr_FR-tom-medium`, débit 0,82, texte écrit pour l'oreille (fluidité) ; prononciations corrigées dans `engine/hx.py`. Musique générée en fond.
- **Charte :** fond `#0B1016`, accent `#2EE6A6`, ambre `#FFB547`, JetBrains Mono + Space Grotesk, signature hexagonale `0x` + `@hexplique`. Pas de logo ni de personnage tiers.
- **Actu :** sujet des 7 derniers jours, ≥ 2 sources fiables, prouvé ≠ allégué, humour sur la situation jamais sur les personnes, label `// veille`, `#veillecyber`.
- **Légende :** accroche, résumé, question, 9–13 hashtags dont `#hexplique #cyber #hack #hacking #hacker`.
- **Limites :** aucun cas client, démos en lab uniquement, mécanisme expliqué sans outil d'attaque prêt à l'emploi.

---

## 4. Historique des Instructions Mémorisées ("Souviens-toi de")

| Date | Instruction / Information mémorisée | Catégorie |
| :--- | :--- | :--- |
| 2026-11-08 | Création du projet : charte, moteur de rendu avec voix Piper intégrée (Tom), fond musical, publication via Windsor. | Gouvernance |
| 2026-11-08 | « reverse » se prononce à l'anglaise (« riverse »). | Production |
| 2026-11-10 | Format actu ajouté, avec ses règles éditoriales. | Éditorial |
| 2026-11-10 | Voix plus fluide : phrases liées, peu de « : », pas de gabarits répétés. | Production |
| 2026-11-12 | Un réel par jour, publication à 10:00 (Paris). | Rythme |
| 2026-11-13 | Hashtags fixes `#cyber #hack #hacking #hacker`. | Éditorial |
| 2026-11-13 | Accroche plus « choc » dans les 2 premières secondes. | Éditorial |
| 2026-11-13 | Stories : passer par le sticker « Questions » (publication manuelle, non supportée par l'API). | Éditorial |
| 2026-11-14 | Hébergement public des vidéos inacceptable → étude de l'upload direct chez Meta. | Sécurité |
| 2026-11-14 | Choix : GitHub Actions ; séparation dev / prod ; token Instagram 60 jours à renouvellement automatisé ; publication déclenchée sur ordre du propriétaire ; Windsor en lecture seule (stats). | Architecture |
| 2026-11-14 | Adoption du cadre `memoire.md` / `TASKS.md` et de la politique zéro-secret. | Gouvernance |
