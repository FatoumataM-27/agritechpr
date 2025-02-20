from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.field import Field
from app import db
from app.utils.logger import log_info, log_error

fields = Blueprint('fields', __name__, url_prefix='/fields')

@fields.route('/')
@login_required
def index():
    user_fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('fields/index.html', fields=user_fields)

@fields.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            surface = request.form.get('surface')
            culture = request.form.get('culture')
            location = request.form.get('location')
            
            if not name or not surface or not culture or not location:
                flash('Tous les champs sont requis.', 'error')
                return redirect(url_for('fields.add'))
            
            new_field = Field(
                name=name,
                surface=float(surface),
                culture=culture,
                location=location,
                user_id=current_user.id
            )
            
            db.session.add(new_field)
            db.session.commit()
            
            log_info(None, f"Nouveau champ ajouté: {name} par {current_user.email}")
            flash('Champ ajouté avec succès!', 'success')
            return redirect(url_for('fields.index'))
            
        except Exception as e:
            log_error(None, f"Erreur lors de l'ajout du champ: {str(e)}")
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'ajout du champ.', 'error')
            return redirect(url_for('fields.add'))
    
    return render_template('fields/add.html')

@fields.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    field = Field.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est propriétaire du champ
    if field.user_id != current_user.id:
        flash('Vous n\'avez pas la permission de modifier ce champ.', 'error')
        return redirect(url_for('fields.index'))
    
    if request.method == 'POST':
        try:
            field.name = request.form.get('name')
            field.surface = float(request.form.get('surface'))
            field.culture = request.form.get('culture')
            field.location = request.form.get('location')
            
            db.session.commit()
            flash('Champ modifié avec succès!', 'success')
            return redirect(url_for('fields.index'))
            
        except Exception as e:
            log_error(None, f"Erreur lors de la modification du champ: {str(e)}")
            db.session.rollback()
            flash('Une erreur est survenue lors de la modification.', 'error')
    
    return render_template('fields/edit.html', field=field)

@fields.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    field = Field.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est propriétaire du champ
    if field.user_id != current_user.id:
        flash('Vous n\'avez pas la permission de supprimer ce champ.', 'error')
        return redirect(url_for('fields.index'))
    
    try:
        db.session.delete(field)
        db.session.commit()
        flash('Champ supprimé avec succès!', 'success')
    except Exception as e:
        log_error(None, f"Erreur lors de la suppression du champ: {str(e)}")
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression.', 'error')
    
    return redirect(url_for('fields.index'))
