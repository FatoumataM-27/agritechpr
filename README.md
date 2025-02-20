# AgriTechPR - Plateforme de Gestion Agricole

## Description du Projet
AgriTechPR est une application web Flask qui aide les agriculteurs à gérer leurs champs, suivre les conditions météorologiques, et planifier leurs tâches agricoles.

## Fonctionnalités Principales
- Gestion des champs agricoles
- Suivi météorologique
- Planification des tâches
- Notifications en temps réel
- Tableau de bord interactif
- Authentification des utilisateurs

## Structure du Projet
```
agritechpr/
├── app/
│   ├── routes/
│   ├── models/
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
├── config.py
└── requirements.txt
```

## Configuration du Développement

### Prérequis
- Python 3.8+
- pip
- virtualenv

### Installation
1. Cloner le repository
```bash
git clone https://github.com/FatoumataM-27/agritechpr.git
cd agritechpr
```

2. Créer et activer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Modifier .env avec vos configurations
```

5. Initialiser la base de données
```bash
flask db upgrade
python init_db.py
```

### Lancer l'application
```bash
flask run
```

## Stratégie de Branches
- `main`: branche de production
- `develop`: branche de développement principale
- `feature/*`: branches pour les nouvelles fonctionnalités
- `bugfix/*`: branches pour les corrections de bugs
- `hotfix/*`: branches pour les corrections urgentes en production

## Workflow de Développement
1. Créer une nouvelle branche depuis `develop`
2. Développer la fonctionnalité
3. Tester localement
4. Créer une Pull Request
5. Review du code
6. Merge dans `develop`

## Tests
```bash
pytest
```

## Déploiement
L'application est configurée pour le déploiement sur Heroku ou un serveur similaire.

## Équipe
- [Membre 1]
- [Membre 2]

## Licence
[Votre licence]
