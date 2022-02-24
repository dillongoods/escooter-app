from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
import logging

app = Flask(__name__)
app.debug = True

app.config.from_object('config')

logging.basicConfig(level=logging.DEBUG)

# Create instance of the database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
from .forms import RegistrationForm

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=RegistrationForm)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_role(name="manager")
    user_datastore.create_role(name="employee")
    user_datastore.create_role(name="customer")

    user_datastore.create_user(email='test@test.net', password='password', roles=['customer'])
    try:
        db.session.commit()
        return 
    except:
        db.session.rollback()