# [NOM DU PROJET] - Registre de Mémoire Persistant

Ce document sert de registre de mémoire persistant pour conserver les directives d'architecture, contraintes techniques, préférences opérationnelles et décisions clés convenues lors des sessions de développement avec l'agent IA.

> **Règle de mise à jour automatique :**
> Dès qu'une consigne commence par ou contient `"souviens toi de <instruction / contenu>"`, l'information doit être immédiatement analysée, structurée et consignée ci-dessous dans la section adéquate et dans le tableau d'historique.

---

## 1. Contexte & Spécifications de l'Environnement

### 🖥️ Environnement Hôte / Cible
- **Nom du projet :** [Ex: Mon Super Projet IA]
- **Type d'infrastructure :** [Ex: Serveur Linux distant / Machine locale / Cluster Docker / Cloud]
- **OS / Distribution :** [Ex: Ubuntu 24.04 LTS / Debian 12]
- **Réseau / Accès :** [Ex: SSH via alias `mon-serveur`, tunnels, adresses locales, etc.]

### 📁 Chemins & Environnements
- **Répertoire de travail :** `[Chemin absolu ou relatif]`
- **Mode d'exécution :** [Ex: Environnement virtuel Python `venv`, conteneurs Docker, etc.]

---

## 2. Principes Fondateurs & Politiques de Sécurité

### 🔒 Politique Stricte Zéro-Secret (Zero-Hardcoded-Secrets)
- **Règle absolue :** Aucun mot de passe, token, URL de webhook, clé API ou clé privée ne doit **JAMAIS** figurer en clair dans le code, les fichiers Markdown, les prompts d'agents, la mémoire ou les commits Git.
- **Principe d'injection :** Les secrets sont injectés **exclusivement** via des variables d'environnement (`os.environ.get(...)`) ou via un fichier `.env` local strictement ignoré.
- **Modèle de référence :** Tout paramètre sensible doit être documenté sans valeur dans un fichier `.env.example`.
- **Fichiers exclus (.gitignore) :** `.env*`, `*.key`, `*.pem`, `*.crt`, dossiers `secrets/`, `credentials/`, logs, backups (`*.bak`), clés SSH privées.
- **Masquage / Sanitization :** En cas d'affichage d'erreurs, logs ou diagnostics, masquer systématiquement les tokens sensibles (ex: `https://.../***`).

---

## 3. Directives Générales de Fonctionnement & Gestion des Tâches

- **Méthodologie d'intervention :** Analyse préalable systématique, structuration modulaire (séparation agents / skills / outillage) et demande de confirmation explicite avant toute action destructive (Human-in-the-Loop).
- **Gestion des Tâches (`TASKS.md`) :**
  - Fichier unique de référence pour le suivi : `TASKS.md`.
  - Mise à jour systématique et automatique à chaque étape de développement (avancement, statut, reste à faire).
  - Déclencheur *"nouvelle tâche : [description]"* : insertion immédiate dans la section *À Réaliser* avec un ID incrémenté, une priorité, une estimation de **complexité** (Faible / Moyenne / Élevée), d'**effort estimé** (durée) et de **budget tokens**.
- **Observabilité LLM :** Maintien d'un suivi de consommation des tokens en en-tête de `TASKS.md` et bilan réel consolidé à la livraison de chaque tâche.

---

## 4. Historique des Instructions Mémorisées ("Souviens-toi de")

| Date | Instruction / Information mémorisée | Catégorie |
| :--- | :--- | :--- |
| YYYY-MM-DD | Initialisation du projet et mise en place des règles de mémoire et zéro-secret. | Gouvernance |
