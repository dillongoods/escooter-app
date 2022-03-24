from app import db, models, app
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from .forms import RegistrationForm


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=RegistrationForm)