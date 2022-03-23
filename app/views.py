from flask import session, render_template, request, redirect, flash, json
from app import app, models, db
from flask_security import current_user, logout_user, auth_required, roles_required
from .forms import StoreCardDetailsForm, CreateBookingForm, LocationForm
import datetime

HIRE_CHOICES = [('1', '1 hr'), ('2', '4 hrs'), ('3', '1 day'), ('4', '1 week')]


def end_active_bookings():
    activeBookings = models.Booking.query.filter_by(is_active=True).all()

    now = datetime.datetime.now().timestamp()

    for item in activeBookings:
        durationInSeconds = item.length * 3600

        if item.time_created.timestamp() + durationInSeconds < now:
            scooter = models.Scooter.query.filter_by(
                id=item.scooter_id).first()

            scooter.availability = True
            item.is_active = False

            db.session.commit()

# Wrapper for render_template to always include whether user is authenticated


def render_template_auth(template, **template_vars):
    return render_template(
        template,
        authenticated=current_user.is_authenticated,
        **template_vars
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template_auth('not_found.html')


@app.route('/', methods=['GET', 'POST'])
@auth_required()
def index():
    end_active_bookings()

    if current_user.has_role('manager'):
        return redirect('/manager')

    return render_template_auth('index.html')


@app.route('/account', methods=['GET'])
@auth_required()
def my_account():
    end_active_bookings()
    # for users to view their account details

    user_email = current_user.email

    user = models.User.query.filter_by(email=user_email).first()
    details = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()

    return render_template_auth('my_account.html', title='My Account', user=user, card_details=details)


@app.route('/account/bank_details', methods=['GET', 'POST'])
@auth_required()
def bank_details():
    end_active_bookings()
    # for users to store their bank details
    #userid = session.get('id')
    #user = models.User.query.filter_by(id=userid).first()

    # if request.method == 'POST':
    details_form = StoreCardDetailsForm()

    if details_form.validate_on_submit():
        details = models.BankDetails(
            name=details_form.name.data,
            accountNo=details_form.accountNo.data,
            sortCode=details_form.sortCode.data,
            expiry=details_form.expiry.data,
            cvc=details_form.cvc.data
        )

        db.session.add(details)
        db.session.commit()
        db.session.flush()

        u = models.User.query.get(current_user.id)
        u.bank_details_id = details.id
        db.session.commit()

        return redirect('/')
        # if user_id is None:
        #     #logging.warning('nothing to process')
        #     return redirect('/')
        # else:
        #     #relationship
        #     db.session.commit()

    return render_template_auth('bank_details.html', title='My Account', form=details_form)


# Hire a scooter
@app.route('/hireScooter', methods=['GET', 'POST'])
def hireScooter():
    end_active_bookings()
    locationName = request.args.get('location')
    scooterId = request.args.get('scooterId')

    allLocations = models.Location.query.all()
    location = models.Location.query.filter_by(name=locationName).first()
    scooter = models.Scooter.query.filter_by(id=scooterId).first()

    if scooter.availability == False:
        return redirect('/')

    user_email = current_user.email
    user = models.User.query.filter_by(email=user_email).first()
    details = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()
    details_form = StoreCardDetailsForm()

    accountNo = str(details.accountNo)[-4:] if details else None

    if details_form.validate_on_submit():
        details = models.BankDetails(
            name=details_form.name.data,
            accountNo=details_form.accountNo.data,
            sortCode=details_form.sortCode.data,
            expiry=details_form.expiry.data,
            cvc=details_form.cvc.data
        )

        db.session.add(details)
        db.session.commit()
        db.session.flush()

        u = models.User.query.get(current_user.id)
        u.bank_details_id = details.id
        db.session.commit()

    return render_template_auth('hireScooter.html', scooter=scooter, location=location, allLocations=allLocations, durationOptions=HIRE_CHOICES, has_card_details=details is not None, details_form=details_form, accountNo=accountNo)

# Perform the hiring


@app.route('/performHire')
def performHire():
    pickupLocationId = int(request.args.get('pickupLocationId'))
    dropoffLocationName = request.args.get('dropoffLocationName')
    durationInHours = int(request.args.get('durationInHours'))
    cost = int(request.args.get('cost'))
    scooterId = int(request.args.get('scooterId'))

    dropoffLocation = models.Location.query.filter_by(
        name=dropoffLocationName).first()

    booking = models.Booking(user_id=current_user.id, scooter_id=scooterId, price=cost,
                             length=durationInHours, pickup=pickupLocationId, dropoff=dropoffLocation.id)

    selectedScooter = models.Scooter.query.filter_by(id=scooterId).first()
    selectedScooter.availability = False

    db.session.add(booking)
    db.session.commit()
    db.session.flush()

    return '200'


@app.route('/confirmHire')
def confirmHire():
    pickupLocationId = int(request.args.get('pickupLocationId'))
    dropoffLocationName = request.args.get('dropoffLocationName')
    durationInHours = int(request.args.get('durationInHours'))
    cost = int(request.args.get('cost'))
    scooterId = int(request.args.get('scooterId'))

    selectedScooter = models.Scooter.query.filter_by(id=scooterId).first()

    pickupLocation = models.Location.query.filter_by(
        id=pickupLocationId).first()
    user = models.User.query.filter_by(id=current_user.id).first()

    bankDetails = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()

    accountNo = str(bankDetails.accountNo)[-4:] if bankDetails else None

    return render_template_auth('confirmHire.html', scooter=selectedScooter, pickupLocationName=pickupLocation.name, dropoffLocationName=dropoffLocationName, cost=cost, durationInHours=durationInHours, accountNo=accountNo)

# Manager Page


@app.route('/manager')
@roles_required('manager')
@auth_required()
def manager():
    end_active_bookings()
    allLocations = models.Location.query.all()

    allScooters = models.Scooter.query.all()

    return render_template_auth('manager/index.html', locations=allLocations, Scooters=allScooters)


@app.route('/manager/add-location', methods=['GET', 'POST'])
@roles_required('manager')
@auth_required()
def managerAddLocation():
    end_active_bookings()
    form = LocationForm()

    if form.validate_on_submit():
        newLocation = models.Location(
            name=form.name.data,
            x_cord=form.x_cord.data,
            y_cord=form.y_cord.data
        )

        db.session.add(newLocation)
        db.session.commit()

        return redirect('/manager')

    return render_template_auth('manager/addLocation.html', form=form, map=map)


# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

# API ---------------------------------------

# Get all locations


@app.route('/api/getLocations')
def getLocations():
    allLocations = models.Location.query.all()

    return json.jsonify({'locations': models.Location.serialize_list(allLocations)})

# Get all scooters in a specific location


@app.route('/api/getScooters')
def getScootersInLocation():
    locationName = request.args.get('location')

    location = models.Location.query.filter_by(name=locationName).first()

    scootersInLocation = models.Scooter.query.filter_by(
        location_id=location.id, availability=True).all()

    return json.jsonify({'scooters': models.Scooter.serialize_list(scootersInLocation)})

# Add a scooter to the location


@app.route('/api/addScooter')
def addScooterToLocation():
    locationId = request.args.get('locationId')

    newScooter = models.Scooter(
        location_id=locationId
    )

    db.session.add(newScooter)
    db.session.commit()

    return '200'



#here need to get the value of hire_choice * how many times its been hired
values = [
    1000, 1300, 900, 850,
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/manager/income')
@roles_required('manager')
@auth_required()
def bar():
    bar_labels= [row[1] for row in HIRE_CHOICES]
    bar_values=values
    return render_template_auth('/manager/income.html', labels=bar_labels, values=bar_values)
