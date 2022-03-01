from email.policy import default
from app import db
from flask_security.models import fsqla_v2 as fsqla

# roles_users = db.Table('roles_users',
#                        db.Column('user_id', db.Integer(),
#                                  db.ForeignKey('users.id')),
#                        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), nullable=True)


class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    fs_uniquifier = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    dob = db.Column(db.Date())
    password = db.Column(db.String(255))
    travel_hours = db.Column(db.Integer(), default=0)
    loyal = db.Column(db.Boolean(), default=False)
    is_discount = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=False)
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('users.id'))
    scooter_id = db.Column('scooter_id', db.Integer(),
                           db.ForeignKey('scooters.id'))
    price = db.Column(db.String(255))
    length = db.Column(db.Integer())
    pickup = db.Column('pickup_location_id', db.Integer(),
                       db.ForeignKey('locations.id'))
    dropoff = db.Column('dropoff_location_id', db.Integer(),
                        db.ForeignKey('locations.id'))


class Scooter(db.Model):
    __tablename__ = 'scooters'
    id = db.Column(db.Integer(), primary_key=True)
    availability = db.Column(db.String(255))
    location_id = db.Column('location_id', db.Integer(),
                            db.ForeignKey('locations.id'))


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    coordinates = db.Column(db.String(255))


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer(), primary_key=True)
    booking_id = db.Column('booking_id', db.Integer(),
                           db.ForeignKey('bookings.id'))
    rating = db.Column(db.Integer())
    message = db.Column(db.String(1000))
    priority = db.Column(db.Integer())


class BankDetails(db.Model):
    __tablename__ = 'bank_details'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    accountNo = db.Column(db.Integer())
    sortCode = db.Column(db.Integer())
    expiry = db.Column(db.Date())
    CVC = db.Column(db.Integer())
