def test_login_page(client):
    """Test que la page de connexion s'affiche correctement"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Se connecter' in response.data

def test_register_page(client):
    """Test que la page d'inscription s'affiche correctement"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Inscription' in response.data

def test_register_user(client):
    """Test l'inscription d'un nouvel utilisateur"""
    response = client.post('/auth/register', data={
        'email': 'nouveau@example.com',
        'name': 'Nouveau User',
        'password': 'motdepasse123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_user(client, test_user):
    """Test la connexion d'un utilisateur"""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_logout(client, test_user):
    """Test la déconnexion d'un utilisateur"""
    # D'abord connecter l'utilisateur
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'motdepasse123'
    })
    
    # Ensuite le déconnecter
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Se connecter' in response.data
