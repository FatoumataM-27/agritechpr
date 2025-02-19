from app import celery_app
from app.models.weather_data import WeatherData
from app.models.field import Field
from app import db
import requests
import json
from datetime import datetime

@celery_app.task
def update_weather_data():
    """Mise à jour des données météo pour tous les champs"""
    fields = Field.query.all()
    api_key = current_app.config['WEATHER_API_KEY']
    
    for field in fields:
        try:
            # Appel à l'API météo
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={field.latitude}&lon={field.longitude}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            # Créer une nouvelle entrée météo
            weather = WeatherData(
                field_id=field.id,
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                description=data['weather'][0]['description'],
                wind_speed=data['wind']['speed'],
                timestamp=datetime.utcnow()
            )
            
            db.session.add(weather)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la mise à jour météo pour le champ {field.id}: {str(e)}")
            continue
    
    return "Mise à jour météo terminée"

@celery_app.task
def send_weather_alerts():
    """Envoie des alertes météo aux agriculteurs"""
    fields = Field.query.all()
    
    for field in fields:
        latest_weather = WeatherData.query.filter_by(field_id=field.id).order_by(WeatherData.timestamp.desc()).first()
        
        if latest_weather:
            # Vérifier les conditions d'alerte
            if latest_weather.temperature > 35:
                send_alert.delay(
                    field.user.email,
                    "Alerte température élevée",
                    f"La température dans votre champ {field.name} est de {latest_weather.temperature}°C"
                )
            
            if latest_weather.humidity < 30:
                send_alert.delay(
                    field.user.email,
                    "Alerte humidité basse",
                    f"L'humidité dans votre champ {field.name} est de {latest_weather.humidity}%"
                )
    
    return "Vérification des alertes terminée"

@celery_app.task
def send_alert(email, subject, message):
    """Envoie un email d'alerte"""
    try:
        # Configuration email
        msg = Message(subject,
                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[email])
        msg.body = message
        mail.send(msg)
        return f"Alerte envoyée à {email}"
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'alerte à {email}: {str(e)}")
        return f"Erreur lors de l'envoi de l'alerte à {email}"
