# 🎓 Projet Python et C – Gestion des Étudiants

Bienvenue dans ce dépôt GitHub qui regroupe deux mini-projets réalisés dans le cadre d’un apprentissage pratique de la programmation.  
L’objectif est d’illustrer l’implémentation d’un même thème – la gestion des étudiants – en **langage Python** et en **langage C**.

---

## 📚 Objectif du projet

Ce projet vise à :

- Appliquer les notions fondamentales de la programmation structurée (C) et orientée objet (Python)
- Comparer les logiques de développement entre un langage bas niveau et un langage haut niveau
- Gérer des données à travers des fichiers
- Renforcer les compétences en algorithmique, en manipulation de fichiers et en structuration de code

---

## 🗂️ Structure du dépôt

Voici la structure des dossiers et fichiers présents dans le dépôt :

```
Projet-Python-et-C/
├── Projet python/
│   ├── gestion_etudiant.py
│   └── ... autres fichiers Python éventuels
│
└── Projet C/
    ├── gestion_etudiant.c
    └── ... fichiers ou headers C supplémentaires
```

Chaque dossier est un projet indépendant mais basé sur le même principe de gestion d'étudiants.

---

## 🐍 Projet Python

Le projet Python est une application console permettant la gestion d’une liste d’étudiants, avec sauvegarde dans un fichier.

### ✅ Fonctionnalités principales :
- ➕ Ajouter un étudiant (nom, matricule, âge, note…)
- 📋 Afficher tous les étudiants enregistrés
- 🔎 Rechercher un étudiant par son nom ou matricule
- 🗑️ Supprimer un étudiant
- 📊 Trier les étudiants par nom ou note
- 💾 Enregistrer et charger la liste d’étudiants à partir d’un fichier

### ▶️ Comment exécuter :
Assurez-vous d’avoir Python installé (version 3.x minimum), puis :

```bash
cd "Projet python"
python gestion_etudiant.py
```

### 📁 Format des fichiers :
- Texte ou JSON pour sauvegarder les étudiants
- Possibilité d’ajouter un menu interactif

---

## 💻 Projet C

Le projet C met en œuvre une application console procédurale pour gérer des étudiants à l’aide de `struct` et de tableaux statiques.

### ✅ Fonctionnalités principales :
- Entrée des informations d’un étudiant
- Affichage complet ou partiel des données
- Recherche par nom ou identifiant
- Gestion d’un tableau d’étudiants
- Écriture et lecture dans des fichiers `.txt`

### ⚙️ Compilation et exécution :
Utilisez un compilateur comme GCC :

```bash
cd "Projet C"
gcc gestion_etudiant.c -o gestion_etudiant
./gestion_etudiant
```

> 🛠️ Le code peut être modifié pour passer à des fichiers binaires ou des listes chaînées.

---

## 🛠️ Technologies utilisées

| Technologie     | Description                                      |
|-----------------|--------------------------------------------------|
| Python 3.x      | Langage de haut niveau pour le projet Python     |
| C               | Langage bas niveau pour le projet procédural     |
| GCC / Clang     | Compilation du projet C                          |
| Git & GitHub    | Gestion de version et hébergement du code        |

---

## 🎯 Objectifs pédagogiques

- Apprendre à structurer un projet logiciel
- Travailler avec des **fichiers texte**, des **structures de données**, et des **algorithmes simples**
- Manipuler des tableaux (C) ou des listes (Python)
- Réaliser une application **interactive et portable**

---

## 📥 Instructions pour cloner ce projet

```bash
git clone https://github.com/7Jacob7/Projet-Python-et-C.git
cd Projet-Python-et-C
```

---

## 📌 Auteur

- **Jacob**  
  Développeur passionné par l'apprentissage pratique de la programmation.  
  🔗 Profil GitHub : [@7Jacob7](https://github.com/7Jacob7)

---

## 📜 Licence

Ce projet est distribué sous la licence **MIT**.  
Vous pouvez l’utiliser, le modifier et le redistribuer librement avec mention de l’auteur.

---

## 🚀 Pistes d'amélioration possibles

Voici quelques idées pour faire évoluer le projet :

- 🔐 Ajouter un système d’authentification (login/mot de passe)
- 📊 Générer des statistiques automatiques (moyenne, note max/min)
- 📈 Ajouter une interface graphique (Tkinter en Python ou SDL en C)
- 🗃️ Intégrer une base de données (SQLite, PostgreSQL)
- 🌐 Convertir la version Python en API web avec Flask

---

## 🤝 Comment contribuer ?

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche : `git checkout -b feature/ma-nouvelle-fonction`
3. Faites vos modifications
4. Poussez vos changements : `git push origin feature/ma-nouvelle-fonction`
5. Créez une **Pull Request**

Merci de respecter le style de code des fichiers existants 🙏

---

## 🙏 Remerciements

Merci à tous les enseignants et encadrants qui encouragent les projets pratiques et la mise en application des cours à travers des cas concrets.

---

> Ce projet montre que la maîtrise d’un même concept peut être explorée de différentes façons selon le langage utilisé. Continuez à apprendre, tester, et créer !

