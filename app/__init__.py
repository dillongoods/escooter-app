from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v2 as fsqla
import logging

MANAGER_EMAIL = 'admin321@gmail.com'

app = Flask(__name__)
app.debug = True


app.config.from_object('config')

logging.basicConfig(level=logging.DEBUG)

# Create instance of the database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
from .forms import RegistrationForm

fsqla.FsModels.set_db_info(db, user_table_name="users", role_table_name="roles")

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=RegistrationForm)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()

    if not user_datastore.find_role("manager"):
        user_datastore.create_role(name="manager")
        user_datastore.create_role(name="employee")

    if not user_datastore.find_user(email=MANAGER_EMAIL):
        user_datastore.create_user(first_name='Admin', last_name='User', email=MANAGER_EMAIL, password="admin1234", roles=["manager"])
    db.session.commit()