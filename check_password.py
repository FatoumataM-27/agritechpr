from app import create_app, db
from app.models.user import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    email = 'fatoumata@gmail.com'
    test_password = 'fatoumata123'
    
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"Utilisateur trouvé: {user.email}")
        print(f"Nom d'utilisateur: {user.username}")
        print(f"Région: {user.region}")
        print(f"Test du mot de passe: {'Correct' if user.check_password(test_password) else 'Incorrect'}")
        print(f"Hash du mot de passe stocké: {user.password_hash}")
    else:
        print(f"Aucun utilisateur trouvé avec l'email: {email}")
