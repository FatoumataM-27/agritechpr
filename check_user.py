from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='fatoumata@gmail.com').first()
    if user:
        print(f"Utilisateur trouvé :")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Region: {user.region}")
    else:
        print("Aucun utilisateur trouvé avec cet email")
