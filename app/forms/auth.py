from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    region = SelectField('Région', choices=[
        ('', 'Sélectionnez votre région...'),
        ('Dakar', 'Dakar'),
        ('Diourbel', 'Diourbel'),
        ('Fatick', 'Fatick'),
        ('Kaffrine', 'Kaffrine'),
        ('Kaolack', 'Kaolack'),
        ('Kédougou', 'Kédougou'),
        ('Kolda', 'Kolda'),
        ('Louga', 'Louga'),
        ('Matam', 'Matam'),
        ('Saint-Louis', 'Saint-Louis'),
        ('Sédhiou', 'Sédhiou'),
        ('Tambacounda', 'Tambacounda'),
        ('Thiès', 'Thiès'),
        ('Ziguinchor', 'Ziguinchor')
    ], validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=6)
    ])
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('S\'inscrire')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired()
    ])
    submit = SubmitField('Se connecter')
