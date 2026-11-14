# Projet de création et publication de contenu pour Instagram.

Ce dossier fournit une **armature universelle, standardisée et éprouvée** pour initialiser rapidement un projet piloté avec des agents IA (Antigravity, Claude, ChatGPT, Cursor, LangGraph, etc.).

Il capitalise sur les meilleures pratiques de gouvernance, d'observabilité des tokens et de politique de sécurité stricte.

---

## 📦 Contenu de la structure

| Fichier | Rôle & Usage |
| :--- | :--- |
| **`memoire.md`** | **Le Registre de Mémoire Persistant.** Déployé sous le nom `memoire.md`. Permet à l'agent IA de conserver les règles de travail, les contraintes d'architecture et d'écouter automatiquement le déclencheur *"souviens toi de ..."*. |
| **`TASKS.md`** | **Le Hub de Suivi des Tâches & Handover.** Déployé sous le nom `TASKS.md`. Centralise l'état d'avancement, le point d'atterrissage entre sessions, le backlog avec complexité/efforts et l'observabilité de la consommation de tokens LLM. |
| **`.env.example`** | Modèle de référence pour les variables d'environnement. Assure la politique **Zéro-Secret**. |
| **`.gitignore`** | Fichier d'exclusion robuste empêchant toute fuite accidentelle de clés privées, tokens, fichiers `.env` ou certificats. |

---

## 💬 Premier Prompt de Démarrage (Humain ou IA)

Dès l'initialisation terminée, ouvrez votre session IA dans le répertoire cible et envoyez :

> *"Bonjour. Nous démarrons un nouveau projet. Prends connaissance des fichiers `memoire.md` et `TASKS.md` à la racine. Ils définissent nos règles de fonctionnement, la politique zéro-secret et notre méthode de suivi des tâches."*

---

## 🌟 Les 4 Piliers Fondamentaux de cette Méthode

1. **Persistance Hors-Contexte (Grounding) :**  
   L'IA ne perd jamais le fil lors des fermetures de sessions grâce au bloc *Handover* et à la lecture systématique de `memoire.md` au démarrage.
2. **Politique Zéro-Secret :**  
   Aucun mot de passe, webhook ou clé privée n'est accepté en dur dans le code ou la doc.
3. **Observabilité des Coûts LLM :**  
   Suivi transparent des tokens d'entrée, de sortie et du taux d'efficience du cache serveur.
4. **Human-in-the-Loop :**  
   Validation préalable obligatoire avant toute opération destructive ou critique.
