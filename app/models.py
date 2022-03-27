from email.policy import default
from app import db
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from flask_security.models import fsqla_v2 as fsqla
from sqlalchemy.inspection import inspect


class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


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
    bank_details_id = db.Column(db.Integer(), db.ForeignKey('bank_details.id'))
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))


class Booking(db.Model, Serializer):
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
    is_active = db.Column(db.Boolean(), default=True)
    time_created = db.Column(DateTime(timezone=True),
                             server_default=func.now())



class BookingViewModel():
    def __init__(self, booking, pickup_location, dropoff_location):
        self.id = booking.id
        self.user_id = booking.user_id
        self.scooter_id = booking.scooter_id
        self.price = booking.price
        self.length = booking.length
        self.pickupLoc = pickup_location
        self.dropoffLoc = dropoff_location
        self.time_created = booking.time_created



class Scooter(db.Model, Serializer):
    __tablename__ = 'scooters'
    id = db.Column(db.Integer(), primary_key=True)
    availability = db.Column(db.Boolean(), default=True)
    location_id = db.Column('location_id', db.Integer(),
                            db.ForeignKey('locations.id'))


class Location(db.Model, Serializer):
    __tablename__ = 'locations'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    x_cord = db.Column(db.String(255))
    y_cord = db.Column(db.String(255))


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer(), primary_key=True)
    booking_id = db.Column('booking_id', db.Integer(),
                           db.ForeignKey('bookings.id'))
    rating = db.Column(db.Integer())
    message = db.Column(db.String(1000))
    priority = db.Column(db.Integer())

class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer(),primary_key=True)
    user_id = db.Column('user_id', db.Integer(),
                            db.ForeignKey('users.id'))
    complaint = db.Column(db.String(1023))

class BankDetails(db.Model):
    __tablename__ = 'bank_details'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    accountNo = db.Column(db.Integer())
    sortCode = db.Column(db.Integer())
    expiry = db.Column(db.Date())
    cvc = db.Column(db.Integer())
