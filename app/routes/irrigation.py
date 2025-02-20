from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, time
from app import db
from app.models.irrigation import IrrigationSystem, IrrigationSchedule, IrrigationLog
from app.models.field import Field

irrigation = Blueprint('irrigation', __name__, url_prefix='/irrigation')

@irrigation.route('/')
@login_required
def index():
    """Liste des systèmes d'irrigation"""
    systems = IrrigationSystem.query.join(Field).filter(Field.user_id == current_user.id).all()
    return render_template('irrigation/index.html', systems=systems)

@irrigation.route('/system/add', methods=['GET', 'POST'])
@login_required
def add_system():
    """Ajouter un nouveau système d'irrigation"""
    if request.method == 'POST':
        try:
            field_id = request.form.get('field_id')
            if not Field.query.get(field_id):
                flash('Champ invalide', 'error')
                return redirect(url_for('irrigation.add_system'))

            system = IrrigationSystem(
                name=request.form.get('name'),
                field_id=field_id,
                type=request.form.get('type'),
                capacity=float(request.form.get('capacity')),
                installation_date=datetime.strptime(request.form.get('installation_date'), '%Y-%m-%d'),
                notes=request.form.get('notes')
            )
            db.session.add(system)
            db.session.commit()
            flash('Système d\'irrigation ajouté avec succès', 'success')
            return redirect(url_for('irrigation.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du système: {str(e)}', 'error')
            return redirect(url_for('irrigation.add_system'))

    fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('irrigation/add_system.html', fields=fields)

@irrigation.route('/system/<int:system_id>')
@login_required
def view_system(system_id):
    """Voir les détails d'un système d'irrigation"""
    system = IrrigationSystem.query.join(Field).filter(
        IrrigationSystem.id == system_id,
        Field.user_id == current_user.id
    ).first_or_404()
    
    schedules = IrrigationSchedule.query.filter_by(system_id=system.id).all()
    logs = IrrigationLog.query.filter_by(system_id=system.id).order_by(IrrigationLog.start_time.desc()).limit(10).all()
    
    return render_template('irrigation/view_system.html', system=system, schedules=schedules, logs=logs)

@irrigation.route('/schedule/add', methods=['POST'])
@login_required
def add_schedule():
    """Ajouter un horaire d'irrigation"""
    try:
        system_id = request.form.get('system_id')
        system = IrrigationSystem.query.join(Field).filter(
            IrrigationSystem.id == system_id,
            Field.user_id == current_user.id
        ).first_or_404()

        schedule = IrrigationSchedule(
            system_id=system.id,
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            duration=int(request.form.get('duration')),
            days=request.form.get('days'),
            water_amount=float(request.form.get('water_amount')) if request.form.get('water_amount') else None
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Horaire d\'irrigation ajouté avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'ajout de l\'horaire: {str(e)}', 'error')
    
    return redirect(url_for('irrigation.view_system', system_id=system_id))

@irrigation.route('/schedule/<int:schedule_id>/toggle', methods=['POST'])
@login_required
def toggle_schedule(schedule_id):
    """Activer/désactiver un horaire d'irrigation"""
    schedule = IrrigationSchedule.query.join(IrrigationSystem).join(Field).filter(
        IrrigationSchedule.id == schedule_id,
        Field.user_id == current_user.id
    ).first_or_404()
    
    try:
        schedule.active = not schedule.active
        db.session.commit()
        status = 'activé' if schedule.active else 'désactivé'
        flash(f'Horaire {status} avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la modification de l\'horaire: {str(e)}', 'error')
    
    return redirect(url_for('irrigation.view_system', system_id=schedule.system_id))

@irrigation.route('/log/add', methods=['POST'])
@login_required
def add_log():
    """Ajouter un log d'irrigation"""
    try:
        system_id = request.form.get('system_id')
        system = IrrigationSystem.query.join(Field).filter(
            IrrigationSystem.id == system_id,
            Field.user_id == current_user.id
        ).first_or_404()

        log = IrrigationLog(
            system_id=system.id,
            start_time=datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M'),
            end_time=datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M') if request.form.get('end_time') else None,
            water_used=float(request.form.get('water_used')) if request.form.get('water_used') else None,
            status=request.form.get('status'),
            notes=request.form.get('notes')
        )
        db.session.add(log)
        db.session.commit()
        flash('Log d\'irrigation ajouté avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'ajout du log: {str(e)}', 'error')
    
    return redirect(url_for('irrigation.view_system', system_id=system_id))

@irrigation.route('/api/system/<int:system_id>/status')
@login_required
def get_system_status(system_id):
    """API pour obtenir le statut d'un système d'irrigation"""
    system = IrrigationSystem.query.join(Field).filter(
        IrrigationSystem.id == system_id,
        Field.user_id == current_user.id
    ).first_or_404()
    
    latest_log = IrrigationLog.query.filter_by(system_id=system.id).order_by(IrrigationLog.start_time.desc()).first()
    
    return jsonify({
        'status': system.status,
        'last_maintenance': system.last_maintenance.isoformat() if system.last_maintenance else None,
        'latest_log': {
            'start_time': latest_log.start_time.isoformat() if latest_log else None,
            'status': latest_log.status if latest_log else None
        }
    })
