from flask import session, render_template, request, redirect, flash, json
from app import app, models, db
from flask_security import current_user, logout_user, auth_required, roles_required
from flask_security.utils import hash_password
from .forms import CancelForm, StoreCardDetailsForm, CreateBookingForm, LocationForm, RegistrationForm, IssueForm
import datetime
from .setup import user_datastore
import smtplib, ssl

HIRE_CHOICES = [('1', '1 hr'), ('2', '4 hrs'), ('3', '1 day'), ('4', '1 week')]


def end_active_bookings():
    activeBookings = models.Booking.query.filter_by(is_active=True).all()

    now = datetime.datetime.now().timestamp()

    for item in activeBookings:
        durationInSeconds = item.length * 3600

        if item.time_created.timestamp() + durationInSeconds < now:
            scooter = models.Scooter.query.filter_by(
                id=item.scooter_id).first()
            scooter.location_id = item.dropoff
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

    return render_template_auth('index.html', isEmployee=current_user.has_role('employee'))


def mapBookingToBookingViewModel(b):
    pickupLocation = models.Location.query.filter_by(
        id=b.pickup).first()
    dropoffLocation = models.Location.query.filter_by(
        id=b.dropoff).first()

    return models.BookingViewModel(b, pickupLocation, dropoffLocation)




@app.route('/setemployee', methods=['GET', 'POST'])
@auth_required()
def set_emplopyee():
    u = models.User.query.filter_by(id=current_user.id).first()
    r = models.Role.query.filter_by(name='employee').first()
    u.roles.append(r)
    db.session.commit()
    db.session.flush()

    return redirect('/')

@app.route('/account', methods=['GET', 'POST'])
@auth_required()
def my_account():
    end_active_bookings()
    # for users to view their account details
    form = CancelForm()

    if request.method == 'POST':
        booking = models.Booking.query.filter_by(id=form.id.data).first()
        selectedScooter = models.Scooter.query.filter_by(
            id=booking.scooter_id).first()
        models.Booking.query.filter_by(id=form.id.data).delete()
        selectedScooter.availability = True
        db.session.commit()
        db.session.flush()

    user_email = current_user.email

    user = models.User.query.filter_by(email=user_email).first()
    details = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()

    a_bookings = models.Booking.query.filter_by(
        user_id=current_user.id, is_active=True)
    active_bookings = map(mapBookingToBookingViewModel, a_bookings)

    p_bookings = models.Booking.query.filter_by(
        user_id=current_user.id, is_active=False)
    previous_bookings = map(mapBookingToBookingViewModel, p_bookings)

    return render_template_auth('my_account.html', title='My Account', user=user, card_details=details, active_bookings=active_bookings, previous_bookings=previous_bookings, form=form)

@app.route('/reportissue', methods=['GET', 'POST'])
@auth_required()
def issue_details():
    #for users to notify staff of any issues
    issue_form = IssueForm()

    if issue_form.validate_on_submit():
        issue = models.Issue(
        user_id = current_user.id,
        complaint = issue_form.complaint.data)

        db.session.add(issue)
        db.session.commit()
        db.session.flush()

    u = models.User.query.get(current_user.id)

    return render_template_auth('submit_issues.html', title='Issue Submission', issue=issue_form)

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

    return render_template_auth('bank_details.html', title='My Account', form=details_form)

# Hire a scooter
@app.route('/employee/hireScooter', methods=['GET', 'POST'])
def employeeHireScooter():

    end_active_bookings()
    locationName = request.args.get('location')
    scooterId = request.args.get('scooterId')

    allLocations = models.Location.query.all()
    location = models.Location.query.filter_by(name=locationName).first()
    scooter = models.Scooter.query.filter_by(id=scooterId).first()

    if scooter.availability == False:
        return redirect('/')

    #user_email = current_user.email
    #user = models.User.query.filter_by(email=user_email).first()
    
    details_form = StoreCardDetailsForm() #

    return render_template_auth('employee/hireScooter.html', scooter=scooter, location=location, allLocations=allLocations, durationOptions=HIRE_CHOICES, details_form=details_form)


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

    details = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()

    accountNo = str(details.accountNo)[-4:] if details else None

    return render_template_auth('hireScooter.html', scooter=scooter, location=location, allLocations=allLocations, durationOptions=HIRE_CHOICES, has_card_details=details is not None, details_form=details_form, accountNo=accountNo)

@app.route('/performHire', methods=['GET'])
def performHire():
    pickupLocationId = int(request.args.get('pickupLocationId'))
    dropoffLocationName = request.args.get('dropoffLocationName')
    durationInHours = int(request.args.get('durationInHours'))
    cost = int(request.args.get('cost'))
    scooterId = int(request.args.get('scooterId'))
    customerEmail = request.args.get('email')

    dropoffLocation = models.Location.query.filter_by(
        name=dropoffLocationName).first()

    if current_user.has_role('employee'):
        booking = models.Booking(user_id=current_user.id, user_email=customerEmail, scooter_id=scooterId, price=cost,
                             length=durationInHours, pickup=pickupLocationId, dropoff=dropoffLocation.id)
    else:    
        booking = models.Booking(user_id=current_user.id, scooter_id=scooterId, price=cost,
                             length=durationInHours, pickup=pickupLocationId, dropoff=dropoffLocation.id)

    selectedScooter = models.Scooter.query.filter_by(id=scooterId).first()
    selectedScooter.availability = False

    db.session.add(booking)
    db.session.commit()
    db.session.flush()

    return '200'


# @app.route('/emailBooking', methods=['GET'])
def emailBooking():
    smtp_server = 'smtp.gmail.com'
    port = 465
    sender = "scooterz.info@gmail.com"
    password = "Sc0oterz123"
    receiver = current_user.email
    userName = current_user.first_name
    message = "Subject: Scooterz Booking Confirmed!\nTo: " + receiver + "\nHi "+userName+", your scooter booking has been confirmed.\nKind Regards,\nScooterz team."

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message)


@app.route('/confirmHire', methods=['GET'])
def confirmHire():
    pickupLocationId = int(request.args.get('pickupLocationId'))
    dropoffLocationName = request.args.get('dropoffLocationName')
    durationInHours = int(request.args.get('durationInHours'))
    cost = int(request.args.get('cost'))
    scooterId = int(request.args.get('scooterId'))
    customerEmail = request.args.get('email')
    guestBank = request.args.get('guestBank')

    selectedScooter = models.Scooter.query.filter_by(id=scooterId).first()

    pickupLocation = models.Location.query.filter_by(
        id=pickupLocationId).first()
    user = models.User.query.filter_by(id=current_user.id).first()

    bankDetails = models.BankDetails.query.filter_by(
        id=user.bank_details_id).first()

    emailBooking()

    if bankDetails:
        accountNo = str(bankDetails.accountNo)[-4:]
    else:
         accountNo = str(guestBank)[-4:]

    return render_template_auth('confirmHire.html', email=customerEmail, scooter=selectedScooter, pickupLocationName=pickupLocation.name, dropoffLocationName=dropoffLocationName, cost=cost, durationInHours=durationInHours, accountNo=accountNo)

# Manager Page


@app.route('/manager')
@roles_required('manager')
@auth_required()
def manager():
    end_active_bookings()
    allLocations = models.Location.query.all()
    allScooters = models.Scooter.query.all()
    employeeRole = models.Role.query.filter_by(name='employee').first()

    employees = [u for u in models.User.query.all() if employeeRole in u.roles]


    bar_labels = [row[1] for row in HIRE_CHOICES]

    oneHourCombinedIncome = getWeekOneHourIncome()
    fourHoursCombinedIncome = getWeekFourHoursIncome()
    dayCombinedIncome = getWeekDayIncome()
    weekCombinedIncome = getWeekWeekIncome()

    values = [oneHourCombinedIncome,
              fourHoursCombinedIncome, dayCombinedIncome, weekCombinedIncome]

    return render_template_auth('manager/index.html', locations=allLocations, Scooters=allScooters, labels=bar_labels, values=values, employees=employees)

@app.route('/manager/add-employee', methods=['GET', 'POST'])
@roles_required('manager')
@auth_required()
def managerAddEmployee():
    end_active_bookings()
    form = RegistrationForm()

    if form.validate_on_submit():
        user_datastore.create_user(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            email=form.email.data,
            password=hash_password(form.password.data),
            roles=["employee"])

        db.session.commit()
        db.session.flush()

        return redirect('/')

    return render_template_auth('manager/add_employee.html', register_user_form=form)


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


def getWeekAgoTimestamp():
    now = datetime.datetime.now().timestamp()
    weekInSeconds = 168 * 3600

    return now - weekInSeconds


def sumPrice(bookings):
    weekAgo = getWeekAgoTimestamp()
    oneHourPrice = 0

    for item in bookings:
        if item.time_created.timestamp() > weekAgo:
            oneHourPrice += int(item.price)

    return oneHourPrice


def getWeekOneHourIncome():
    bookingsOneHour = models.Booking.query.filter_by(
        is_active=False, length=1).all()

    return sumPrice(bookingsOneHour)


def getWeekFourHoursIncome():
    bookingsFourHours = models.Booking.query.filter_by(
        is_active=False, length=4).all()

    return sumPrice(bookingsFourHours)


def getWeekDayIncome():
    bookingsOneDay = models.Booking.query.filter_by(
        is_active=False, length=24).all()

    return sumPrice(bookingsOneDay)


def getWeekWeekIncome():
    bookingsOneWeek = models.Booking.query.filter_by(
        is_active=False, length=168).all()

    return sumPrice(bookingsOneWeek)
