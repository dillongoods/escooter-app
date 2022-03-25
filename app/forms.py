from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SelectField, PasswordField, HiddenField, validators
from wtforms.validators import DataRequired
from flask_security import RegisterForm

HIRE_CHOICES = [('1', '1 hr'), ('2', '4 hrs'), ('3', '1 day'), ('4', '1 week')]
PRIORITY_CHOICES = [('1', 'low'), ('2', 'high')]
RATING_CHOICES = [('1', '1 star'), ('2', '2 stars'),
                  ('3', '3 stars'), ('4', '4 stars'), ('5', '5 stars')]
LOCATION_CHOICES = [('1', 'Trinity Centre'), ('2', 'Train Station'),
                    ('3', 'Merrion Centre'), ('4', 'LGI'), ('5', 'The Edge')]


class RegistrationForm(RegisterForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    dob = DateField('Date of Birth')


class StoreCardDetailsForm(FlaskForm):
    id = StringField('id')
    name = StringField('name', validators=[DataRequired()])
    accountNo = IntegerField('accountno', validators=[DataRequired()])
    sortCode = IntegerField('sortCode', validators=[DataRequired()])
    expiry = DateField('expiry', validators=[DataRequired()])
    cvc = IntegerField('cvc', validators=[DataRequired()])


class CreateBookingForm(FlaskForm):
    id = StringField('id')
    scooterid = StringField('scooterid')
    cost = IntegerField('cost')
    hirePeriod = SelectField(
        u'Hire period', choices=HIRE_CHOICES, validators=[DataRequired()])
    pickupLoc = SelectField(
        u'Pickup location', choices=LOCATION_CHOICES, validators=[DataRequired()])
    dropOffLoc = SelectField(u'Dropoff location', choices=LOCATION_CHOICES)
    email = StringField('Email Address', validators=[DataRequired()])


class FeedbackForm(FlaskForm):
    id = StringField('id')
    rating = SelectField(u'rating', choices=RATING_CHOICES,
                         validators=[DataRequired()])
    message = StringField('message', validators=[DataRequired()])
    priority = SelectField(
        'priority', choices=PRIORITY_CHOICES, validators=[DataRequired()])

class LocationForm(FlaskForm):
    id = StringField('id')
    name = StringField('name',  validators=[DataRequired()])
    x_cord = StringField('x_cord',  validators=[DataRequired()])
    y_cord = StringField('y_cord',  validators=[DataRequired()])

class CancelForm(FlaskForm):
	id = StringField('id')