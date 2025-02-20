from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.field import Field
from app.models.task import Task
from app.models.notification import Notification
from app.models.weather_data import WeatherData
from app.models.field_growth import FieldGrowth
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        # Récupérer les champs de l'utilisateur
        fields = Field.query.filter_by(user_id=current_user.id).all()
        
        # Récupérer les tâches en cours (non terminées)
        tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status != 'terminée'
        ).order_by(Task.due_date).limit(5).all()

        # Récupérer les données météo les plus récentes
        weather_data = WeatherData.query.filter_by(city='Vélingara').order_by(WeatherData.timestamp.desc()).first()

        # Initialiser les valeurs par défaut si weather_data est None
        weather = {
            'temperature': 30,
            'humidity': 60,
            'precipitation_probability': 60,
            'wind_speed': 10,
            'solar_radiation': 800
        }

        if weather_data:
            weather.update({
                'temperature': weather_data.temperature,
                'humidity': weather_data.humidity,
                'precipitation_probability': weather_data.precipitation_probability,
                'wind_speed': weather_data.wind_speed,
                'solar_radiation': weather_data.solar_radiation
            })

        return render_template('dashboard.html',
                             user=current_user,
                             fields=fields,
                             tasks=tasks,
                             weather=weather)
                             
    except Exception as e:
        flash('Une erreur est survenue lors du chargement du tableau de bord.', 'error')
        return redirect(url_for('main.index'))

@main.route('/fields')
@login_required
def fields():
    try:
        fields = Field.query.filter_by(user_id=current_user.id).all()
        return render_template('fields.html', fields=fields)
    except Exception as e:
        flash('Une erreur est survenue lors du chargement des champs.', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/fields/add', methods=['POST'])
@login_required
def add_field():
    try:
        name = request.form.get('name')
        size = request.form.get('size')
        crop_type = request.form.get('crop_type')
        soil_type = request.form.get('soil_type', 'limoneux')
        irrigation_system = request.form.get('irrigation_system', 'non disponible')
        drainage_system = request.form.get('drainage_system', 'non disponible')
        topography = request.form.get('topography', 'plat')
        
        if not all([name, size, crop_type]):
            flash('Les champs nom, taille et type de culture sont requis', 'error')
            return redirect(url_for('main.fields'))
        
        try:
            size = float(size)
        except ValueError:
            flash('La taille doit être un nombre', 'error')
            return redirect(url_for('main.fields'))
        
        field = Field(
            name=name,
            size=size,
            crop_type=crop_type,
            soil_type=soil_type,
            irrigation_system=irrigation_system,
            drainage_system=drainage_system,
            topography=topography,
            user_id=current_user.id
        )
        
        db.session.add(field)
        db.session.commit()
        flash('Champ ajouté avec succès!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Une erreur est survenue lors de l\'ajout du champ', 'error')
    
    return redirect(url_for('main.fields'))

@main.route('/fields/<int:field_id>')
@login_required
def field_details(field_id):
    try:
        field = Field.query.get_or_404(field_id)
        
        # Vérifier que le champ appartient à l'utilisateur
        if field.user_id != current_user.id:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('main.fields'))
        
        # Récupérer les données de croissance
        growth_data = FieldGrowth.query.filter_by(
            field_id=field.id
        ).order_by(FieldGrowth.recorded_at.desc()).all()
        
        # Récupérer les tâches associées au champ
        tasks = Task.query.filter_by(
            field_id=field.id
        ).order_by(Task.due_date).all()
        
        # Récupérer les données météo
        weather_data = WeatherData.query.filter_by(city='Vélingara').order_by(WeatherData.timestamp.desc()).first()

        # Initialiser les valeurs par défaut
        field_weather = {
            'temperature': 30,
            'humidity': 60,
            'precipitation_probability': 20,
            'wind_speed': 10,
            'condition': 'Ensoleillé'
        }

        if weather_data:
            field_weather.update({
                'temperature': weather_data.temperature,
                'humidity': weather_data.humidity,
                'precipitation_probability': weather_data.precipitation_probability,
                'wind_speed': weather_data.wind_speed,
                'condition': weather_data.condition
            })
        
        return render_template('field_details.html',
                             field=field,
                             growth_data=growth_data,
                             field_tasks=tasks,
                             field_weather=field_weather,
                             today=datetime.utcnow())
                             
    except Exception as e:
        flash('Une erreur est survenue lors du chargement des détails du champ.', 'error')
        return redirect(url_for('main.fields'))

@main.route('/fields/<int:field_id>/growth')
@login_required
def field_growth(field_id):
    field = Field.query.get_or_404(field_id)
    
    # Vérifier que le champ appartient à l'utilisateur
    if field.user_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.fields'))
    
    # Récupérer les données de croissance sur les 30 derniers jours
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    growth_data = FieldGrowth.query.filter(
        FieldGrowth.field_id == field.id,
        FieldGrowth.recorded_at >= thirty_days_ago
    ).order_by(FieldGrowth.recorded_at.asc()).all()
    
    # Préparer les données pour le graphique
    dates = [g.recorded_at.strftime('%Y-%m-%d') for g in growth_data]
    heights = [g.height for g in growth_data]
    health_scores = [g.health_score for g in growth_data]
    
    return render_template('field_growth.html',
                         field=field,
                         growth_data=growth_data)

@main.route('/fields/<int:field_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_field(field_id):
    field = Field.query.get_or_404(field_id)
    
    # Vérifier que le champ appartient à l'utilisateur
    if field.user_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.fields'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        size = request.form.get('size')
        crop_type = request.form.get('crop_type')
        soil_type = request.form.get('soil_type')
        irrigation_system = request.form.get('irrigation_system')
        drainage_system = request.form.get('drainage_system')
        topography = request.form.get('topography')
        
        if not all([name, size, crop_type]):
            flash('Les champs nom, taille et type de culture sont requis', 'error')
            return redirect(url_for('main.edit_field', field_id=field.id))
        
        try:
            size = float(size)
        except ValueError:
            flash('La taille doit être un nombre', 'error')
            return redirect(url_for('main.edit_field', field_id=field.id))
        
        try:
            field.name = name
            field.size = size
            field.crop_type = crop_type
            field.soil_type = soil_type
            field.irrigation_system = irrigation_system
            field.drainage_system = drainage_system
            field.topography = topography
            
            db.session.commit()
            flash('Champ mis à jour avec succès!', 'success')
            return redirect(url_for('main.field_details', field_id=field.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la mise à jour du champ', 'error')
            return redirect(url_for('main.edit_field', field_id=field.id))
    
    return render_template('fields/edit.html', field=field)

@main.route('/tasks')
@login_required
def tasks():
    try:
        # Récupérer les tâches de l'utilisateur
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
        
        # Calculer les jours restants pour chaque tâche
        for task in tasks:
            task.days = task.days_remaining()
        
        # Récupérer les champs pour le formulaire d'ajout
        fields = Field.query.filter_by(user_id=current_user.id).all()
        
        return render_template('tasks.html', tasks=tasks, fields=fields)
    except Exception as e:
        flash('Une erreur est survenue lors du chargement des tâches.', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    try:
        title = request.form.get('title')
        field_id = request.form.get('field_id')
        due_date = request.form.get('due_date')
        description = request.form.get('description')
        priority = request.form.get('priority', 'moyenne')
        
        if not all([title, field_id, due_date]):
            flash('Le titre, le champ et la date d\'échéance sont requis', 'error')
            return redirect(url_for('main.tasks'))
        
        # Vérifier que le champ appartient à l'utilisateur
        field = Field.query.get_or_404(field_id)
        if field.user_id != current_user.id:
            flash('Champ non valide', 'error')
            return redirect(url_for('main.tasks'))
        
        # Créer la tâche
        task = Task(
            title=title,
            description=description or '',
            due_date=datetime.strptime(due_date, '%Y-%m-%d'),
            field_id=field_id,
            user_id=current_user.id,
            priority=priority,
            status='à faire'
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Tâche ajoutée avec succès!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Une erreur est survenue lors de l\'ajout de la tâche: {str(e)}', 'error')
    
    return redirect(url_for('main.tasks'))

@main.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.completed = True
        db.session.commit()
        flash('Tâche marquée comme terminée!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/data')
@login_required
def data():
    region = request.args.get('region', 'Tambacounda')
    weather_data = {
        'temperature': 32,
        'humidity': 65,
        'wind_speed': 12,
        'precipitation': 0,
        'forecast': [
            {'day': 'Lundi', 'temp': 31, 'condition': 'Ensoleillé'},
            {'day': 'Mardi', 'temp': 33, 'condition': 'Partiellement nuageux'},
            {'day': 'Mercredi', 'temp': 30, 'condition': 'Risque de pluie'}
        ]
    }
    return render_template('data.html', region=weather_data)

@main.route('/api/weather')
@login_required
def get_weather():
    city = request.args.get('city', 'Vélingara')
    return jsonify({
        'temperature': 32,
        'humidity': 65,
        'wind_speed': 12,
        'precipitation': 0,
        'precipitation_probability': 60
    })

@main.route('/api/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications])

@main.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    notification_ids = request.json.get('notification_ids', [])
    if notification_ids:
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user.id
        ).update({Notification.read: True}, synchronize_session=False)
        db.session.commit()
    return jsonify({'success': True})

@main.route('/support')
def support():
    return render_template('support.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')
