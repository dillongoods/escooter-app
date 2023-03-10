from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security.models import fsqla_v2 as fsqla
from flask_security.utils import hash_password
import logging

MANAGER_EMAIL = 'admin321@gmail.com'

app = Flask(__name__)
app.debug = True


app.config.from_object('config')

logging.basicConfig(level=logging.DEBUG)

# Create instance of the database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

fsqla.FsModels.set_db_info(db, user_table_name="users", role_table_name="roles")

from app import views, models, setup

from .setup import user_datastore, add_locations, add_scooters

@app.before_first_request
def setup_admin():
    db.create_all()

    # add_locations()
    # add_scooters()

    if not user_datastore.find_role("manager"):
        user_datastore.create_role(name="manager")
        user_datastore.create_role(name="employee")

    if not user_datastore.find_user(email=MANAGER_EMAIL):
        user_datastore.create_user(first_name='Admin', last_name='User', email=MANAGER_EMAIL, password=hash_password("admin1234"), roles=["manager"])
    db.session.commit()

