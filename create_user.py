from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Créer un nouvel utilisateur
    user = User(
        username='fatoumata',
        email='fatoumata@gmail.com',
        region='Dakar',
        ville='Dakar'
    )
    user.set_password('password123')
    
    # Ajouter l'utilisateur à la base de données
    db.session.add(user)
    db.session.commit()
    
    print(f"Utilisateur créé avec succès : {user.email}")
