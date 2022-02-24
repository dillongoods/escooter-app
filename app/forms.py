from flask_wtf import Form
from wtforms import IntegerField, DateField, StringField, SelectField
from wtforms.validators import DataRequired
from flask_security.forms import RegisterForm

HIRE_CHOICES = [('1', '1 hr'), ('2', '4 hrs'), ('3', '1 day'), ('4', '1 week')]
PRIORITY_CHOICES = [('1', 'low'), ('2', 'high')]
RATING_CHOICES = [('1', '1 star'), ('2', '2 stars'),
                  ('3', '3 stars'), ('4', '4 stars'), ('5', '5 stars')]
LOCATION_CHOICES = [('1', 'Trinity Centre'), ('2', 'Train Station'),
                    ('3', 'Merrion Centre'), ('4', 'LGI'), ('5', 'The Edge')]


class RegistrationForm(RegisterForm):
    firstName = StringField('First name', validators=[DataRequired()])
    lastName = StringField('Last name', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])


class StoreCardDetails(Form):
    id = StringField('id')
    firstName = StringField('firstName', validators=[DataRequired()])
    lastName = StringField('lastName', validators=[DataRequired()])
    accountNo = IntegerField('accountno', validators=[DataRequired()])
    sortCode = IntegerField('sortCode', validators=[DataRequired()])
    expiry = DateField('expiry', validators=[DataRequired()])
    CVC = IntegerField('CVC', validators=[DataRequired()])


class CreateBooking(Form):
    id = StringField('id')
    scooterid = StringField('scooterid')
    hirePeriod = SelectField(
        u'period', choices=HIRE_CHOICES, validators=[DataRequired()])
    pickupLoc = SelectField(
        u'pickup', choices=LOCATION_CHOICES, validators=[DataRequired()])
    dropOffLoc = SelectField(u'dropoff', choices=LOCATION_CHOICES)


class Feedback(Form):
    id = StringField('id')
    rating = SelectField(u'rating', choices=RATING_CHOICES,
                         validators=[DataRequired()])
    message = StringField('message', validators=[DataRequired()])
    priority = SelectField(
        'priority', choices=PRIORITY_CHOICES, validators=[DataRequired()])
