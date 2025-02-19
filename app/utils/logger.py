import os
import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            if hasattr(request, 'user'):
                record.user = request.user.email
            else:
                record.user = 'Anonymous'
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.user = None
            
        return super().format(record)

def setup_logger(app):
    """Configure le système de logging de l'application"""
    
    # Création du handler pour le fichier
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Configuration du niveau de logging
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgriTechPro startup')

def log_info(app, message):
    """Log un message de niveau INFO"""
    if app:
        app.logger.info(message)
    else:
        logging.info(message)

def log_error(app, error):
    """Log une erreur avec le contexte complet"""
    if app:
        app.logger.error(f'Error: {str(error)}', exc_info=True)
    else:
        logging.error(f'Error: {str(error)}', exc_info=True)

def log_warning(app, message):
    """Log un message de niveau WARNING"""
    if app:
        app.logger.warning(message)
    else:
        logging.warning(message)

def log_debug(app, message):
    """Log un message de debug avec le contexte de la requête"""
    if app:
        app.logger.debug(message)
    else:
        logging.debug(message)
