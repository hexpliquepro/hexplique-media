# hexplique - Suivi des Tâches & Observabilité

Ce document centralise l'état d'avancement des développements, le point de reprise entre sessions (*Handover*), les tâches en cours, le backlog à réaliser, le suivi de consommation des tokens LLM et l'historique des travaux terminés.

> Le calendrier éditorial détaillé (épisode par épisode) reste dans `CALENDRIER.md` (dépôt `hexplique`).

---

## 📊 Métriques Globales de Consommation LLM (Session)
- **Modèle actif :** Claude (Cowork) — identifiant configuré `claude-opus-5-5`
- **Appels Modèle (Steps/Invocations) :** non mesuré
- **Tokens Entrants (Prompt/In) :** non mesuré
- **Tokens Sortants (Génération/Out) :** non mesuré
- **Tokens Lus depuis le Cache (Context Caching) :** non mesuré
- **Efficience :** non mesurée
> L'agent n'a pas accès aux compteurs réels : seules des estimations sont possibles, signalées comme telles.

---

## 📍 Point d'Atterrissage / Reprise de Session (Handover)
> Ce bloc sert de "mémoire tampon" entre deux sessions de chat pour reprendre le travail sans perte de contexte.

- **Dernière session :** 2026-11-14
- **Actions livrées lors de cette session :**
  - Réels publiés : A03 (panne Outlook), A04 (SignDrop), 03 (masque et sous-réseaux, programmé puis publié le 14/11 à 10:00).
  - Story S01 (appel à thématiques) : deux visuels, dont un fond pour sticker « Questions ».
  - Consigne d'accroche « choc » ajoutée à `CLAUDE.md`.
  - Vue d'architecture et des échanges GitHub / Windsor / Instagram.
  - Étude « upload direct chez Meta via GitHub Actions » ; choix du propriétaire enregistrés.
  - Gabarits `memoire.md`, `TASKS.md`, `README.md` déposés puis renseignés.
- **Priorités prêtes pour la prochaine session :**
  - **T-01** : validation du réel A05 (dim. 15/11 10:00).
  - **T-02** : publication directe chez Meta, dès que les prérequis sont levés.
- **Points d'attention / Prérequis pour la reprise :**
  - T-02 en attente de l'installation par le propriétaire (`publisher/README.md`), puis d'un essai réel.
  - `memoire.md` / `TASKS.md` sont dans un dépôt **public** : n'y rien écrire de sensible (T-05).
  - Ne rien déployer sans autorisation explicite du propriétaire.

---

## 📌 Tableau de Bord Synthétique

| ID | Tâche | Priorité | Complexité | Effort Est. | Tokens (Est. / Réel) | Statut | Rôle / Composant |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **R-xx** | Production quotidienne des réels (récurrent) | Haute | 🟡 Moyenne | ~45 min / réel | ~80k / — | 🔁 Récurrent | `reels/`, `CALENDRIER.md` |
| **T-01** | Valider le réel A05 (Grok Build) | Haute | 🟢 Faible | ~5 min (propriétaire) | ~5k / — | ✅ Validé le 14/11, publication programmée dim. 15/11 10:00 | `reels/A05-grok-apps` |
| **T-02** | Publication directe chez Meta via GitHub Actions (deux dépôts) | Haute | 🔴 Élevée | ~4-6h | ~150k / — | 🟡 Code prêt, en attente installation propriétaire | `publisher/`, `hexplique-publish` |
| **T-03** | Renouvellement automatique du token Instagram (GitHub App) | Haute | 🟡 Moyenne | ~1h30 | ~50k / — | 🟡 Code prêt et testé (dans T-02), activation à l’installation | `publisher/` |
| **T-04** | Fin de l'hébergement public (hexplique-media privé ou supprimé) | Haute | 🟢 Faible | ~15 min | ~10k / — | ⚪ À faire (après T-02) | GitHub |
| **T-05** | Registres dans un dépôt privé | Haute | 🟢 Faible | — | — | 🔵 Réglé par T-04 (hexplique-media devient privé) | GitHub |
| **T-06** | Windsor en lecture seule : procédure + éventuelle restriction des permissions | Moyenne | 🟢 Faible | ~30 min | ~15k / — | ⚪ À faire (après T-02) | `CLAUDE.md`, Windsor |
| **T-07** | Story S01 : publication manuelle + collecte des réponses | Moyenne | 🟢 Faible | ~15 min | ~10k / — | 🟠 En attente propriétaire | `stories/` |
| **T-08** | Comparatif d'audience actu vs notions (stats Windsor) | Moyenne | 🟡 Moyenne | ~1h | ~40k / — | ⚪ À faire (≥ 48 h de recul) | Windsor (lecture) |
| **T-09** | Nouveau format inspiré de rick.theengineer, avec notre DA | Moyenne | 🔴 Élevée | ~3h+ | ~100k / — | 🟠 En attente précisions | Éditorial, moteur |
| **T-10** | Templates de l'organisation « pas lundi » | Moyenne | 🟢 Faible | ~30 min | ~20k / — | 🟠 En attente invitation | GitHub |

---

## 🚀 En Cours (In Progress)

### [T-02] Publication directe chez Meta via GitHub Actions
- **Objectif :** supprimer toute URL publique : le runner GitHub envoie le MP4 validé directement chez Meta (upload resumable), sur clic du propriétaire.
- **Composant :** `hexplique-media` (privé à terme : branche `content` = file d'attente, `publisher/` = code proposé) ; `hexplique-publish` (privé, compte personnel du propriétaire : workflows + secrets).
- **Complexité / Effort :** 🔴 Élevée (~4-6h)
- **Budget Tokens Estimé :** ~150 k tokens
- **Avancement :**
  - [x] Étude d'architecture, comparatif des options, limites du plan gratuit vérifiées (pas d'environnements ni de relecteurs sur dépôt privé)
  - [x] Choix validés : GitHub Actions, deux dépôts, clic du propriétaire, token Instagram 60 jours renouvelé automatiquement, Windsor en lecture seule, purge de `content` sur approbation
  - [x] Code préparé dans `publisher/` : publication, rotation, santé, alertes, 5 workflows, `.env.example`, `.gitignore`, guide d'installation
  - [x] Tests hors ligne (APIs Meta et GitHub simulées) : 11/11
  - [x] Outil de file d'attente `tools/content_queue.py` (dépôt `hexplique`) testé en local
  - [ ] Installation par le propriétaire (dépôt, clé de déploiement, app Meta + token, GitHub App) — voir `publisher/README.md`
  - [ ] Essai réel (mode « essai ») : confirmer que l'upload resumable accepte un token Instagram Login (doc Meta ambiguë, repli Facebook Login prévu)
  - [ ] Bascule : procédure dans `CLAUDE.md`, tâche planifiée de production, notification « prêt à publier »
  - [ ] Privatisation de hexplique-media par le propriétaire (T-04)
- **Reste à faire :** installation par le propriétaire, puis essai réel.
- **Statut :** 🟡 En cours (55%)

---

## 📋 À Réaliser (Backlog / Todo)

### [T-01] Valider le réel A05
- **Objectif :** réel actu « 35 000 applis Grok Build ouvertes : un lien n'est pas un mot de passe », produit le 14/11 par la tâche planifiée.
- **Complexité / Effort :** 🟢 Faible (~5 min, propriétaire)
- **Budget Tokens Estimé :** ~5 k tokens
- **Reste à faire :** « Je valide l'épisode A05 », puis publication programmée dim. 15/11 à 10:00.
- **Statut :** 🟠 En attente propriétaire

### [T-03] Renouvellement automatique du token Instagram
- **Objectif :** workflow hebdomadaire qui renouvelle le token (60 jours) et réécrit le secret GitHub via une GitHub App limitée au dépôt de publication (droit « Secrets : écriture » uniquement).
- **Complexité / Effort :** 🟡 Moyenne (~1h30)
- **Budget Tokens Estimé :** ~50 k tokens
- **Reste à faire :** après T-02 ; alerte en cas d'échec.
- **Statut :** ⚪ À faire (0%)

### [T-04] Fin de l'hébergement public des vidéos
- **Objectif :** passer hexplique-media en privé ou le supprimer une fois T-02 en production.
- **Complexité / Effort :** 🟢 Faible (~15 min, action du propriétaire)
- **Budget Tokens Estimé :** ~10 k tokens
- **Reste à faire :** après bascule ; les MP4 déjà publics ont pu être copiés.
- **Statut :** ⚪ À faire (0%)

### [T-05] Déplacer `memoire.md` / `TASKS.md` dans un dépôt privé
- **Objectif :** ces registres décrivent l'architecture et les décisions ; ils ne doivent pas rester publics.
- **Complexité / Effort :** 🟢 Faible (~10 min)
- **Budget Tokens Estimé :** ~10 k tokens
- **Reste à faire :** choix du dépôt cible par le propriétaire (`hexplique` ou futur dépôt de publication).
- **Statut :** ⚪ À faire (0%)

### [T-06] Windsor en lecture seule
- **Objectif :** retirer toute action d'écriture de la procédure ; vérifier si les permissions Meta de Windsor peuvent être réduites à la lecture.
- **Complexité / Effort :** 🟢 Faible (~30 min)
- **Budget Tokens Estimé :** ~15 k tokens
- **Reste à faire :** après T-02.
- **Statut :** ⚪ À faire (0%)

### [T-07] Story S01 — appel à thématiques
- **Objectif :** Le propriétaire publie le fond depuis l'app avec le sticker « Questions » ; les réponses alimentent `CALENDRIER.md`.
- **Complexité / Effort :** 🟢 Faible (~15 min)
- **Budget Tokens Estimé :** ~10 k tokens
- **Reste à faire :** publication par le propriétaire, transmission des réponses.
- **Statut :** 🟠 En attente propriétaire

### [T-08] Comparatif d'audience actu vs notions
- **Objectif :** comparer vues, taux de visionnage complet, partages et enregistrements des notions (01–03) et des actus (A01–A04) à 48 h et à 7 jours.
- **Complexité / Effort :** 🟡 Moyenne (~1h)
- **Budget Tokens Estimé :** ~40 k tokens
- **Reste à faire :** collecte via Windsor ; biais à signaler (3 réels le 13/11, horaires différents).
- **Statut :** ⚪ À faire (0%)

### [T-09] Format inspiré de rick.theengineer, avec notre DA
- **Objectif :** proposer un format propre à hexplique (ex. mascotte originale autour du « 0x »), sans personnage tiers.
- **Complexité / Effort :** 🔴 Élevée (~3h+)
- **Budget Tokens Estimé :** ~100 k tokens
- **Reste à faire :** Le propriétaire précise ce qui l'intéresse (format, ton, mascotte).
- **Statut :** 🟠 En attente précisions

### [T-10] Templates de l'organisation « pas lundi »
- **Objectif :** récupérer les templates partagés par le propriétaire.
- **Complexité / Effort :** 🟢 Faible (~30 min)
- **Budget Tokens Estimé :** ~20 k tokens
- **Reste à faire :** acceptation de l'invitation par le compte hexpliquepro (impossible avec les outils de l'agent), puis noms des dépôts à rattacher à la session.
- **Statut :** 🟠 En attente invitation

---

## ✅ Réalisé (Done / Historique)

### [T-00] Mise en place du projet et du moteur
- **Livré :** charte, logo, polices, `CALENDRIER.md`, `CLAUDE.md`, moteur `engine/hx.py` (scènes calées sur la voix, sous-titres incrustés), voix Piper Tom, fond musical `engine/music.py`, publication Windsor via GitHub Pages.
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-08

### [T-00b] Réels publiés
- **Livré :** 00 présentation (v3), 01 modèle OSI, A01 honey trap, 02 adresse IP, A02 Outlook NTLM, A03 panne Outlook, A04 SignDrop, 03 masque et sous-réseaux (identifiants dans `CALENDRIER.md`).
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-08 → 2026-11-14

### [T-00c] Règles éditoriales et de production
- **Livré :** format actu, fluidité de la voix, rythme quotidien à 10:00, hashtags fixes, accroche « choc », prononciations.
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-10 → 2026-11-13

### [T-00d] Story S01 (visuels)
- **Livré :** visuel avec réponse en message privé + fond pour sticker « Questions ».
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-13

### [T-00e] Études d'architecture
- **Livré :** vue d'ensemble de la chaîne et des accès, détail des échanges GitHub / Windsor / Instagram, comparatif d'hébergement privé, étude de l'upload direct chez Meta via GitHub Actions (dev / prod, rotation de token).
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-14

### [T-00f] Cadre méthodologique
- **Livré :** dépôt des gabarits `memoire.md`, `TASKS.md`, `README.md` ; adoption des règles (mémoire, zéro-secret, suivi des tâches).
- **Consommation réelle mesurée :** non mesurée
- **Date :** 2026-11-14
