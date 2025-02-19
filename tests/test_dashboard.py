import pytest
from datetime import datetime
from app.models.field import Field
from app.models.task import Task
from app.models.weather_data import WeatherData

def test_dashboard_access_without_login(client):
    """Test l'accès au tableau de bord sans connexion"""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirection vers login
    assert '/auth/login' in response.location

def test_dashboard_access_with_login(client, test_user):
    """Test l'accès au tableau de bord avec connexion"""
    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_dashboard_fields_display(client, test_user, test_field):
    """Test l'affichage des champs dans le tableau de bord"""
    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert test_field.name.encode() in response.data
    assert str(test_field.area).encode() in response.data

def test_dashboard_tasks_display(client, test_user):
    """Test l'affichage des tâches dans le tableau de bord"""
    # Créer une tâche de test
    task = Task(
        title="Tâche test",
        description="Description de la tâche test",
        due_date=datetime.utcnow(),
        user_id=test_user.id
    )
    from app import db
    db.session.add(task)
    db.session.commit()

    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert task.title.encode() in response.data

def test_dashboard_weather_display(client, test_user):
    """Test l'affichage des données météo dans le tableau de bord"""
    # Créer des données météo de test
    weather = WeatherData(
        temperature=25.5,
        humidity=65,
        description="Ensoleillé",
        location="Dakar",
        user_id=test_user.id
    )
    from app import db
    db.session.add(weather)
    db.session.commit()

    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"25.5" in response.data
    assert b"Ensoleill" in response.data

def test_add_field(client, test_user):
    """Test l'ajout d'un nouveau champ"""
    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    # Ajouter un nouveau champ
    response = client.post('/fields/add', data={
        'name': 'Nouveau champ',
        'area': 150.5,
        'crop_type': 'Maïs'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Nouveau champ" in response.data
    assert b"150.5" in response.data

def test_add_task(client, test_user):
    """Test l'ajout d'une nouvelle tâche"""
    # Connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    # Ajouter une nouvelle tâche
    response = client.post('/tasks/add', data={
        'title': 'Nouvelle tâche',
        'description': 'Description de la nouvelle tâche',
        'due_date': '2025-03-01'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Nouvelle t\xc3\xa2che" in response.data
