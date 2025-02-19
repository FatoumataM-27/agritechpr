import json

def test_get_fields(client, test_user, test_field):
    """Test la récupération de la liste des champs"""
    response = client.get('/api/v1/fields')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Field'

def test_create_field(client, test_user):
    """Test la création d'un nouveau champ"""
    response = client.post('/api/v1/fields', json={
        'name': 'Nouveau Champ',
        'area': 150.0,
        'crop_type': 'Riz'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Nouveau Champ'
    assert data['area'] == 150.0

def test_get_single_field(client, test_user, test_field):
    """Test la récupération d'un champ spécifique"""
    response = client.get(f'/api/v1/fields/{test_field.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Field'

def test_update_field(client, test_user, test_field):
    """Test la mise à jour d'un champ"""
    response = client.put(f'/api/v1/fields/{test_field.id}', json={
        'name': 'Champ Modifié',
        'area': 200.0
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Champ Modifié'
    assert data['area'] == 200.0

def test_delete_field(client, test_user, test_field):
    """Test la suppression d'un champ"""
    response = client.delete(f'/api/v1/fields/{test_field.id}')
    assert response.status_code == 204
    
    # Vérifier que le champ a bien été supprimé
    response = client.get(f'/api/v1/fields/{test_field.id}')
    assert response.status_code == 404
