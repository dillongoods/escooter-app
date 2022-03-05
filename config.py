import os

DEBUG = True
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'tothemoon'
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = 'tothemoon'
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = False
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
SECURITY_LOGOUT_METHODS=["GET", "POST"]
WTF_CSRF_ENABLED = True
