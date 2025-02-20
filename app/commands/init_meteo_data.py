import click
from flask.cli import with_appcontext
from app import db
from app.models.meteo_region import MeteoRegion

@click.command('init-meteo')
@with_appcontext
def init_meteo_command():
    """Initialise les données météo de test"""
    # Supprime les données existantes
    MeteoRegion.query.delete()

    # Données de test pour différentes régions
    regions_data = [
        {
            'region': 'Tambacounda',
            'temperature': 30,
            'precipitations': 58,
            'humidite': 30,
            'vent': 15,
            'rayonnement': 13
        },
        {
            'region': 'Dakar',
            'temperature': 28,
            'precipitations': 45,
            'humidite': 75,
            'vent': 20,
            'rayonnement': 18
        },
        {
            'region': 'Saint-Louis',
            'temperature': 26,
            'precipitations': 35,
            'humidite': 70,
            'vent': 25,
            'rayonnement': 15
        }
    ]

    # Ajoute les données de test
    for data in regions_data:
        region = MeteoRegion(**data)
        db.session.add(region)

    db.session.commit()
    click.echo('Données météo initialisées avec succès !')
