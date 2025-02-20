from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from app.services.meteo_service import MeteoService
from app.models.meteo_region import MeteoRegion
from app.models.region_favorite import RegionFavorite
from app import db

region_data = Blueprint('region_data', __name__, url_prefix='/data')

@region_data.route('/')
@login_required
def show_data():
    regions = list(current_app.config['REGIONS_COORDINATES'].keys())
    favorites = RegionFavorite.query.filter_by(user_id=current_user.id).all()
    
    return render_template('region_data.html',
                         regions=regions,
                         regions_favorites=favorites)

@region_data.route('/api/meteo/<region>')
@login_required
def get_meteo_data(region):
    try:
        meteo_data = MeteoService.get_weather_data(region)
        if meteo_data:
            return jsonify(meteo_data)
        return jsonify({'erreur': 'Données non disponibles pour cette région'})
    except Exception as e:
        return jsonify({'erreur': str(e)})

@region_data.route('/favoris/ajouter', methods=['POST'])
@login_required
def add_favorite():
    region = request.form.get('region')
    notes = request.form.get('notes', '')
    
    if not region:
        return jsonify({'erreur': 'Région non spécifiée'})
        
    existing = RegionFavorite.query.filter_by(
        user_id=current_user.id,
        region=region
    ).first()
    
    if existing:
        return jsonify({'erreur': 'Cette région est déjà dans vos favoris'})
        
    try:
        favorite = RegionFavorite(
            user_id=current_user.id,
            region=region,
            notes=notes
        )
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erreur': str(e)})

@region_data.route('/favoris/supprimer/<int:favori_id>', methods=['DELETE'])
@login_required
def remove_favorite(favori_id):
    favorite = RegionFavorite.query.get_or_404(favori_id)
    
    if favorite.user_id != current_user.id:
        return jsonify({'erreur': 'Non autorisé'}), 403
        
    try:
        db.session.delete(favorite)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'erreur': str(e)})
