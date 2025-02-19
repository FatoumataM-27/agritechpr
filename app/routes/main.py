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
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        # Récupérer les données météo les plus récentes
        weather_data = WeatherData.query.filter_by(city='Vélingara').order_by(WeatherData.timestamp.desc()).first()
        
        # Récupérer les champs de l'utilisateur
        fields = Field.query.filter_by(user_id=current_user.id).all()
        
        # Récupérer les tâches en cours
        tasks = Task.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).order_by(Task.due_date).limit(5).all()

        # Initialiser les valeurs par défaut si weather_data est None
        weather_context = {
            'temperature': 30,
            'humidity': 60,
            'precipitation_probability': 60,
            'wind_speed': 10,
            'solar_radiation': 800
        }

        if weather_data:
            weather_context = {
                'temperature': weather_data.temperature,
                'humidity': weather_data.humidity,
                'precipitation_probability': weather_data.precipitation_probability,
                'wind_speed': weather_data.wind_speed,
                'solar_radiation': weather_data.solar_radiation
            }

        return render_template('dashboard.html',
            user=current_user,
            weather=weather_context,
            fields=fields,
            tasks=tasks
        )
    except Exception as e:
        print(f"Erreur dans le dashboard: {str(e)}")
        flash("Une erreur est survenue lors du chargement du tableau de bord.")
        return redirect(url_for('main.index'))

@main.route('/fields')
@login_required
def fields():
    fields = Field.query.filter_by(user_id=current_user.id).all()
    return render_template('fields.html', fields=fields)

@main.route('/fields/add', methods=['POST'])
@login_required
def add_field():
    if request.method == 'POST':
        name = request.form.get('name')
        area = request.form.get('area')
        location = request.form.get('location')
        crop_type = request.form.get('crop_type')
        planting_date = request.form.get('planting_date')
        
        if not all([name, area, location, crop_type, planting_date]):
            flash('Tous les champs sont requis', 'error')
            return redirect(url_for('main.fields'))
        
        try:
            area = float(area)
            planting_date = datetime.strptime(planting_date, '%Y-%m-%d')
        except ValueError:
            flash('Format invalide pour la surface ou la date', 'error')
            return redirect(url_for('main.fields'))
        
        field = Field(name=name, area=area, location=location,
                     crop_type=crop_type, planting_date=planting_date,
                     user_id=current_user.id)
        
        db.session.add(field)
        db.session.commit()
        
        flash('Champ ajouté avec succès!', 'success')
        return redirect(url_for('main.fields'))

@main.route('/fields/<int:field_id>')
@login_required
def field_details(field_id):
    field = Field.query.get_or_404(field_id)
    
    # Vérifier que le champ appartient à l'utilisateur
    if field.user_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.fields'))
    
    # Récupérer les données de croissance
    growth_data = FieldGrowth.query.filter_by(
        field_id=field.id
    ).order_by(FieldGrowth.date.desc()).all()
    
    # Récupérer les tâches associées au champ
    tasks = Task.query.filter_by(
        field_id=field.id
    ).order_by(Task.due_date).all()
    
    return render_template('field_details.html',
                         field=field,
                         growth_data=growth_data,
                         field_tasks=tasks,
                         today=datetime.utcnow())

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
        FieldGrowth.date >= thirty_days_ago
    ).order_by(FieldGrowth.date.asc()).all()
    
    # Préparer les données pour le graphique
    dates = [g.date.strftime('%Y-%m-%d') for g in growth_data]
    heights = [g.height for g in growth_data]
    health_scores = [g.health_score for g in growth_data]
    
    return render_template('field_growth.html',
                         field=field,
                         growth_data=growth_data)

@main.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    return render_template('tasks.html', tasks=tasks)

@main.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        field_id = request.form.get('field_id')
        
        task = Task(title=title, description=description,
                   due_date=datetime.strptime(due_date, '%Y-%m-%d'),
                   field_id=field_id, user_id=current_user.id)
        
        db.session.add(task)
        db.session.commit()
        
        flash('Tâche ajoutée avec succès!', 'success')
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
