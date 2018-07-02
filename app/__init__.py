from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging #python package, DEBUG, INFO, WARNING, ERROR and CRITICAL
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login' #would use in a url_for() call to get the URL.
mail = Mail(app)
bootstrap = Bootstrap(app)
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '160139164703343',
        'secret': '4a005ebc42acab187de54ba991ef3ea6'
    },
    'google': {
        'id': '160139164703343',
        'secret': '4a005ebc42acab187de54ba991ef3ea6'
    }
}
from app import routes,models, errors

if not app.debug:
	if app.config['MAIL_SERVER']:
		auth = None
		if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
			auth=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']: #Transport Layer Security 
			secure=()
		mail_handler = SMTPHandler(
			mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr = 'no-reply@'+app.config['MAIL_SERVER'],
			toaddrs = app.config['ADMINS'], subject='Microblog Failure',
			credentials = auth, secure=secure
			)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)
	if not os.path.exists('logs'):
		os.mkdir('logs')
	file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)

	app.logger.addHandler(logging.INFO)
	app.logger.info('Microblog startup')