from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(email='fatoumata@gmail.com').first():
        print("L'utilisateur existe déjà")
    else:
        # Créer un nouvel utilisateur
        new_user = User(
            email='fatoumata@gmail.com',
            username='fatoumata',
            region='Dakar',  # Vous pouvez changer la région si nécessaire
            ville='Dakar'    # Vous pouvez changer la ville si nécessaire
        )
        new_user.set_password('fatoumata123')  # Mot de passe temporaire
        
        # Sauvegarder dans la base de données
        try:
            db.session.add(new_user)
            db.session.commit()
            print("Compte créé avec succès!")
            print("\nVos identifiants de connexion:")
            print("Email: fatoumata@gmail.com")
            print("Mot de passe: fatoumata123")
            print("\nVeuillez changer votre mot de passe après la connexion.")
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création du compte: {str(e)}")
