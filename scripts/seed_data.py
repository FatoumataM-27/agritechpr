from app import create_app, db
from app.models.user import User
from app.models.field import Field
from app.models.task import Task
from app.models.notification import Notification
from app.models.weather_data import WeatherData
from app.models.field_growth import FieldGrowth
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

app = create_app()

def create_test_data():
    with app.app_context():
        # Nettoyer la base de données
        db.drop_all()
        db.create_all()
        
        # Créer un utilisateur de test
        user = User(
            username="fatou",
            email="fatou@example.com",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        
        # Créer des champs
        fields = [
            Field(
                name="Champ de Riz",
                size=10.0,
                crop_type="Riz",
                soil_type="Limoneux",
                irrigation_system="Disponible",
                drainage_system="Disponible",
                topography="Plat",
                user_id=user.id
            ),
            Field(
                name="Champ de Mil",
                size=8.0,
                crop_type="Mil",
                soil_type="Argileux",
                irrigation_system="Non disponible",
                drainage_system="Disponible",
                topography="Vallonné",
                user_id=user.id
            ),
            Field(
                name="Champ de Maïs",
                size=5.0,
                crop_type="Maïs",
                soil_type="Sableux",
                irrigation_system="Disponible",
                drainage_system="Non disponible",
                topography="Plat",
                user_id=user.id
            )
        ]
        
        for field in fields:
            db.session.add(field)
        db.session.commit()
        
        # Créer des tâches
        tasks = [
            Task(
                title="Arroser les 3 hectares du champ de riz",
                description="Utiliser le système d'irrigation pour arroser la partie nord du champ",
                due_date=datetime.utcnow() + timedelta(days=3),
                field_id=fields[0].id,
                user_id=user.id
            ),
            Task(
                title="Désherber le champ de mil",
                description="Enlever les mauvaises herbes qui commencent à pousser",
                due_date=datetime.utcnow() + timedelta(days=5),
                field_id=fields[1].id,
                user_id=user.id
            ),
            Task(
                title="Appliquer l'engrais sur le maïs",
                description="Utiliser l'engrais organique sur tout le champ",
                due_date=datetime.utcnow() + timedelta(days=7),
                field_id=fields[2].id,
                user_id=user.id
            )
        ]
        
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        
        # Créer des notifications
        notifications = [
            Notification(
                message="De fortes chaleurs sont à prévoir demain",
                type="warning",
                user_id=user.id
            ),
            Notification(
                message="N'oubliez pas de vérifier l'irrigation du champ de riz",
                type="info",
                user_id=user.id
            ),
            Notification(
                message="Des pluies sont prévues ce lundi, pensez à protéger vos récoltes",
                type="alert",
                user_id=user.id
            )
        ]
        
        for notif in notifications:
            db.session.add(notif)
        db.session.commit()
        
        # Créer des données météo
        cities = ["Vélingara", "Kolda", "Tambacounda"]
        for city in cities:
            weather = WeatherData(
                region="Kolda" if city == "Vélingara" else city,
                city=city,
                temperature=random.uniform(28.0, 35.0),
                humidity=random.uniform(50.0, 70.0),
                precipitation_probability=random.uniform(30.0, 80.0),
                wind_speed=random.uniform(10.0, 30.0),
                solar_radiation=random.uniform(5.0, 15.0)
            )
            db.session.add(weather)
        db.session.commit()
        
        # Créer des données de croissance
        months = ["Avril", "Mai", "Juin", "Juillet", "Août", "Septembre"]
        for field in fields:
            for i, month in enumerate(months):
                # Simuler une croissance progressive
                base_score = 5.0
                variation = random.uniform(-0.5, 1.5)
                growth = FieldGrowth(
                    field_id=field.id,
                    growth_score=min(10.0, base_score + (i * 0.8) + variation),
                    month=month,
                    year=2024
                )
                db.session.add(growth)
        db.session.commit()
        
        print("Données de test créées avec succès!")
        print(f"Utilisateur créé : fatou@example.com / password123")
        print(f"Nombre de champs créés : {len(fields)}")
        print(f"Nombre de tâches créées : {len(tasks)}")
        print(f"Nombre de notifications créées : {len(notifications)}")

if __name__ == "__main__":
    create_test_data()
