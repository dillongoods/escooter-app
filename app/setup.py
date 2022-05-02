from app import db, models, app
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from .forms import RegistrationForm


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, register_form=RegistrationForm)

def add_locations():
    locations = [
        models.Location(name="Trinity centre", y_cord="53.79673582921463", x_cord="-1.5444995000000001"),
        models.Location(name="Train station", y_cord="53.79458173891782", x_cord="-1.5475380861418773"),
        models.Location(name="Merrion centre", y_cord="53.80153576066675", x_cord="-1.5442298726504184"),
        models.Location(name="LGI hospital", y_cord="53.80265079409744", x_cord="-1.5529133591591897"),
        models.Location(name="UoL Edge sports centre", y_cord="53.80421869533736", x_cord="-1.5532317303228644")
    ]

    db.session.add_all(locations)

    db.session.commit()

def add_scooters():
    db.session.flush()

    A = models.Location.query.filter_by(name="Trinity centre").first().id
    B = models.Location.query.filter_by(name="Train station").first().id
    C = models.Location.query.filter_by(name="Merrion centre").first().id
    D = models.Location.query.filter_by(name="LGI hospital").first().id
    E = models.Location.query.filter_by(name="UoL Edge sports centre").first().id

    scooters = [
        models.Scooter(availability=True, location_id=A),
        models.Scooter(availability=True, location_id=A),
        models.Scooter(availability=True, location_id=A),
        models.Scooter(availability=True, location_id=A),
        models.Scooter(availability=True, location_id=B),
        models.Scooter(availability=True, location_id=B),
        models.Scooter(availability=True, location_id=B),
        models.Scooter(availability=True, location_id=B),
        models.Scooter(availability=True, location_id=C),
        models.Scooter(availability=True, location_id=C),
        models.Scooter(availability=True, location_id=C),
        models.Scooter(availability=True, location_id=C),
        models.Scooter(availability=True, location_id=D),
        models.Scooter(availability=True, location_id=D),
        models.Scooter(availability=True, location_id=D),
        models.Scooter(availability=True, location_id=D),
        models.Scooter(availability=True, location_id=E),
        models.Scooter(availability=True, location_id=E),
        models.Scooter(availability=True, location_id=E),
        models.Scooter(availability=True, location_id=E),
    ]

    db.session.add_all(scooters)

    db.session.commit()