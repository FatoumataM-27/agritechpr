# AgriTechPro - Plateforme de Gestion Agricole

## 📱 Description
AgriTechPro est une application web moderne conçue pour aider les agriculteurs sénégalais à gérer efficacement leurs exploitations agricoles. Elle offre des fonctionnalités de suivi des champs, de gestion des tâches et d'accès aux données météorologiques.

## 🚀 Fonctionnalités

### Gestion des utilisateurs
- Inscription et connexion sécurisée
- Gestion de profil utilisateur
- Authentification avec Flask-Login

### Gestion des champs
- Ajout et suivi des champs
- Visualisation des données de croissance
- Cartographie des parcelles

### Suivi météorologique
- Données météo en temps réel
- Prévisions personnalisées
- Alertes météo

### Gestion des tâches
- Planification des activités agricoles
- Suivi des tâches
- Notifications et rappels

## 🛠 Technologies utilisées
- **Backend**: Python/Flask
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Base de données**: SQLite avec SQLAlchemy
- **Authentification**: Flask-Login
- **API**: Flask-RESTful (en cours)

## 📦 Installation

1. Cloner le repository
```bash
git clone https://github.com/FatoumataM-27/agritechpro.git
cd agritechpro
```

2. Créer un environnement virtuel
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
```

6. Lancer l'application
```bash
flask run
```

## 🌳 Structure du projet
```
agritechpro/
├── app/
│   ├── models/          # Modèles de données
│   ├── routes/          # Routes et contrôleurs
│   ├── templates/       # Templates HTML
│   └── __init__.py     # Configuration Flask
├── migrations/         # Migrations de base de données
├── tests/             # Tests unitaires et d'intégration
├── config.py          # Configuration
├── requirements.txt   # Dépendances
└── run.py            # Point d'entrée
```

## 👥 Équipe
- Développeur 1 (@dev1)
- Développeur 2 (@dev2)

## 📝 License
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
