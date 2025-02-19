import pytest
from app import create_app, db
from app.models.user import User
from app.models.field import Field

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    user = User(
        email='test@example.com',
        name='Test User',
        password='sha256$abc123'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_field(app, test_user):
    field = Field(
        name='Test Field',
        area=100.0,
        crop_type='Maïs',
        user_id=test_user.id
    )
    db.session.add(field)
    db.session.commit()
    return field
