# [NOM DU PROJET] - Suivi des Tâches & Observabilité

Ce document centralise l'état d'avancement des développements, le point de reprise entre sessions (*Handover*), les tâches en cours, le backlog à réaliser, le suivi de consommation des tokens LLM et l'historique des travaux terminés.

---

## 📊 Métriques Globales de Consommation LLM (Session)
- **Modèle actif :** [Ex: Gemini 3.8 Flash / Claude 3.5 Sonnet / Qwen 2.5 Coder]
- **Appels Modèle (Steps/Invocations) :** 0
- **Tokens Entrants (Prompt/In) :** 0 k tokens
- **Tokens Sortants (Génération/Out) :** 0 k tokens
- **Tokens Lus depuis le Cache (Context Caching) :** 0 k tokens
- **Efficience :** [Pourcentage de tokens issus du cache]

---

## 📍 Point d'Atterrissage / Reprise de Session (Handover)
> Ce bloc sert de "mémoire tampon" entre deux sessions de chat pour reprendre le travail sans perte de contexte.

- **Dernière session :** YYYY-MM-DD - HH:MM
- **Actions livrées lors de cette session :**
  - [Résumé de ce qui a été achevé et validé lors de la session précédente]
- **Priorités prêtes pour la prochaine session :**
  - **T-01** : [Prochaine tâche prioritaire à entamer]
  - **T-02** : [Seconde tâche candidate]
- **Points d'attention / Prérequis pour la reprise :**
  - [Ex: Vérifier que le tunnel SSH est ouvert / que l'environnement virtuel est activé]

---

## 📌 Tableau de Bord Synthétique

| ID | Tâche | Priorité | Complexité | Effort Est. | Tokens (Est. / Réel) | Statut | Rôle / Composant |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **T-01** | [Nom de la première tâche] | Haute | 🟢 Faible | ~30 min | ~25k / — | ⚪ À faire | [Rôle / Module] |
| **T-02** | [Nom de la seconde tâche] | Moyenne | 🟡 Moyenne | ~1h | ~40k / — | ⚪ À faire | [Rôle / Module] |
| **T-03** | [Nom de la troisième tâche] | Haute | 🔴 Élevée | ~2h-3h | ~70k / — | ⚪ À faire | [Rôle / Module] |

---

## 🚀 En Cours (In Progress)

### [T-0X] [Titre de la tâche en cours]
- **Objectif :** [Description claire et résultat attendu]
- **Composant :** [Dossier / Module concerné]
- **Complexité / Effort :** [🟢 Faible / 🟡 Moyenne / 🔴 Élevée] (~X min/heures)
- **Budget Tokens Estimé :** ~XX k tokens
- **Avancement :**
  - [x] Étape 1 réalisée
  - [ ] Étape 2 en cours
  - [ ] Étape 3 à faire
- **Reste à faire :** [Points bloquants ou actions restantes]
- **Statut :** 🟡 En cours (X%)

---

## 📋 À Réaliser (Backlog / Todo)

### [T-01] [Titre de la tâche]
- **Objectif :** [Description]
- **Complexité / Effort :** 🟢 Faible (~30 min)
- **Budget Tokens Estimé :** ~25 k tokens
- **Reste à faire :** [Détail des actions attendues]
- **Statut :** ⚪ À faire (0%)

### [T-02] [Titre de la tâche]
- **Objectif :** [Description]
- **Complexité / Effort :** 🟡 Moyenne (~1h)
- **Budget Tokens Estimé :** ~40 k tokens
- **Reste à faire :** [Détail des actions attendues]
- **Statut :** ⚪ À faire (0%)

---

## ✅ Réalisé (Done / Historique)

### [T-00] Initialisation du cadre méthodologique
- **Livré :** Mise en place des registres `memoire.md`, `TASKS.md`, `.gitignore` et `.env.example`.
- **Consommation réelle mesurée :** ~XX k tokens
- **Date :** YYYY-MM-DD
