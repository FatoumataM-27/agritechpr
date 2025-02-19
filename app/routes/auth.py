from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Veuillez vérifier vos identifiants et réessayer.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Vérification des champs requis
        if not email or not name or not password:
            flash('Tous les champs sont requis.')
            return redirect(url_for('auth.register'))

        # Vérification si l'email existe déjà
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Cet email est déjà enregistré')
            return redirect(url_for('auth.register'))

        # Création du nouvel utilisateur
        try:
            new_user = User(
                email=email,
                name=name,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Connexion automatique après inscription
            login_user(new_user)
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.')
            print(f"Erreur d'inscription: {str(e)}")
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
