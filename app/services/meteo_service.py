import requests
from flask import current_app
from datetime import datetime, timedelta
from app import db
from app.models.meteo_region import MeteoRegion
from app.utils.logger import log_info, log_error

class MeteoService:
    @staticmethod
    def get_weather_data(region):
        """Récupère les données météo pour une région donnée"""
        try:
            # Vérifier si nous avons des données récentes en cache (moins de 30 minutes)
            donnees_cache = MeteoRegion.query.filter_by(region=region).first()
            if donnees_cache and (datetime.utcnow() - donnees_cache.date_mise_a_jour) < timedelta(minutes=30):
                log_info(None, f"Utilisation des données en cache pour {region}")
                return donnees_cache.to_dict()

            # Récupérer les coordonnées de la région
            coords = current_app.config['REGIONS_COORDINATES'].get(region)
            if not coords:
                log_error(None, f"Coordonnées non trouvées pour la région: {region}")
                return None

            # Récupérer la clé API
            api_key = current_app.config.get('OPENWEATHER_API_KEY')
            if not api_key:
                log_error(None, "Clé API OpenWeatherMap non configurée")
                return donnees_cache.to_dict() if donnees_cache else None

            # Appeler l'API OpenWeatherMap
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': api_key,
                'units': 'metric',
                'lang': 'fr'
            }
            
            log_info(None, f"Appel API OpenWeatherMap pour {region}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Récupérer les prévisions pour les précipitations
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Calculer la probabilité de précipitations
            rain_prob = 0
            if forecast_data['list']:
                rain_count = sum(1 for item in forecast_data['list'][:8] if 'rain' in item)
                rain_prob = (rain_count / 8) * 100

            # Convertir les données
            donnees_meteo = {
                'region': region,
                'temperature': round(data['main']['temp']),
                'humidite': data['main']['humidity'],
                'vent': round(data['wind']['speed'] * 3.6),  # Conversion en km/h
                'precipitations': round(rain_prob),  # Probabilité de pluie en pourcentage
                'rayonnement': round(100 - data['clouds']['all']),  # Inverse de la couverture nuageuse
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }

            # Mettre à jour ou créer l'entrée dans la base de données
            if not donnees_cache:
                donnees_cache = MeteoRegion(region=region)
                db.session.add(donnees_cache)

            # Mettre à jour les données
            for key, value in donnees_meteo.items():
                if hasattr(donnees_cache, key):
                    setattr(donnees_cache, key, value)
            
            donnees_cache.date_mise_a_jour = datetime.utcnow()
            db.session.commit()
            
            log_info(None, f"Données météo mises à jour pour {region}")
            return donnees_meteo

        except requests.RequestException as e:
            log_error(None, f"Erreur lors de l'appel à l'API météo: {str(e)}")
            return donnees_cache.to_dict() if donnees_cache else None
        except Exception as e:
            log_error(None, f"Erreur inattendue: {str(e)}")
            return donnees_cache.to_dict() if donnees_cache else None

    @staticmethod
    def get_all_regions():
        """Récupère la liste des régions disponibles"""
        return list(current_app.config['REGIONS_COORDINATES'].keys())
