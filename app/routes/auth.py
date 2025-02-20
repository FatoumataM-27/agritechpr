from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
from app.utils.logger import log_info, log_error

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        print(f"Tentative de connexion pour l'email: {email}")  # Debug log
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Aucun utilisateur trouvé avec l'email: {email}")  # Debug log
            flash('Veuillez vérifier vos identifiants et réessayer.')
            return redirect(url_for('auth.login'))

        if not user.check_password(password):
            print(f"Mot de passe incorrect pour l'utilisateur: {email}")  # Debug log
            flash('Veuillez vérifier vos identifiants et réessayer.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        print(f"Connexion réussie pour l'utilisateur: {email}")  # Debug log
        log_info(None, f"Connexion réussie pour {user.email}")
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            region = request.form.get('region')
            ville = request.form.get('ville')

            # Vérification des champs requis
            if not email or not username or not password or not region or not ville:
                flash('Tous les champs sont requis.')
                return redirect(url_for('auth.register'))

            # Vérification de la longueur du mot de passe
            if len(password) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères.')
                return redirect(url_for('auth.register'))

            # Vérification si l'email existe déjà
            if User.query.filter_by(email=email).first():
                flash('Cet email est déjà enregistré.')
                return redirect(url_for('auth.register'))

            # Vérification si le nom d'utilisateur existe déjà
            if User.query.filter_by(username=username).first():
                flash('Ce nom d\'utilisateur est déjà pris.')
                return redirect(url_for('auth.register'))

            # Création du nouvel utilisateur
            new_user = User(
                email=email,
                username=username,
                region=region,
                ville=ville
            )
            new_user.set_password(password)

            # Ajout à la base de données
            db.session.add(new_user)
            db.session.commit()

            # Connecter automatiquement l'utilisateur après l'inscription
            login_user(new_user)
            
            log_info(None, f"Nouvel utilisateur inscrit : {email} ({region}, {ville})")
            flash('Inscription réussie ! Bienvenue sur votre tableau de bord.')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            log_error(None, f"Erreur lors de l'inscription : {str(e)}")
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.')
    return redirect(url_for('main.index'))
