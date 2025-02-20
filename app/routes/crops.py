from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.crop import Crop
from app.models.crop_activity import CropActivity
from app.models.field import Field

crops = Blueprint('crops', __name__, url_prefix='/crops')

@crops.route('/')
@login_required
def index():
    """Page principale des cultures"""
    user_crops = Crop.query.filter_by(user_id=current_user.id).all()
    fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('crops/index.html', crops=user_crops, fields=fields)

@crops.route('/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    """Ajouter une nouvelle culture"""
    if request.method == 'POST':
        try:
            field_id = request.form.get('field_id')
            if not Field.query.get(field_id):
                flash('Champ invalide', 'error')
                return redirect(url_for('crops.add_crop'))

            crop = Crop(
                user_id=current_user.id,
                name=request.form.get('name'),
                variety=request.form.get('variety'),
                planting_date=datetime.strptime(request.form.get('planting_date'), '%Y-%m-%d'),
                expected_harvest_date=datetime.strptime(request.form.get('expected_harvest_date'), '%Y-%m-%d') if request.form.get('expected_harvest_date') else None,
                field_id=field_id,
                notes=request.form.get('notes')
            )
            db.session.add(crop)
            db.session.commit()
            flash('Culture ajoutée avec succès', 'success')
            return redirect(url_for('crops.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de la culture: {str(e)}', 'error')
            return redirect(url_for('crops.add_crop'))

    fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('crops/add.html', fields=fields)

@crops.route('/<int:crop_id>')
@login_required
def view_crop(crop_id):
    """Voir les détails d'une culture"""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    activities = CropActivity.query.filter_by(crop_id=crop.id).order_by(CropActivity.date.desc()).all()
    return render_template('crops/view.html', crop=crop, activities=activities)

@crops.route('/<int:crop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_crop(crop_id):
    """Modifier une culture"""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            crop.name = request.form.get('name')
            crop.variety = request.form.get('variety')
            crop.planting_date = datetime.strptime(request.form.get('planting_date'), '%Y-%m-%d')
            crop.expected_harvest_date = datetime.strptime(request.form.get('expected_harvest_date'), '%Y-%m-%d') if request.form.get('expected_harvest_date') else None
            crop.notes = request.form.get('notes')
            crop.status = request.form.get('status')
            
            db.session.commit()
            flash('Culture mise à jour avec succès', 'success')
            return redirect(url_for('crops.view_crop', crop_id=crop.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour de la culture: {str(e)}', 'error')
    
    fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('crops/edit.html', crop=crop, fields=fields)

@crops.route('/<int:crop_id>/activity/add', methods=['POST'])
@login_required
def add_activity(crop_id):
    """Ajouter une activité à une culture"""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    
    try:
        activity = CropActivity(
            crop_id=crop.id,
            activity_type=request.form.get('activity_type'),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            quantity=float(request.form.get('quantity')) if request.form.get('quantity') else None,
            unit=request.form.get('unit'),
            notes=request.form.get('notes'),
            created_by=current_user.id
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activité ajoutée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'ajout de l\'activité: {str(e)}', 'error')
    
    return redirect(url_for('crops.view_crop', crop_id=crop.id))

@crops.route('/api/list')
@login_required
def api_list_crops():
    """API pour lister les cultures (utilisé pour la recherche)"""
    crops = Crop.query.filter_by(user_id=current_user.id).all()
    return jsonify([crop.to_dict() for crop in crops])
