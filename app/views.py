from flask import session, render_template, request, redirect, flash, json
from app import app, models, db
from flask_security import current_user, logout_user, auth_required, roles_required
from .forms import StoreCardDetailsForm, CreateBookingForm, LocationForm
# from flask_googlemaps import GoogleMaps, Map
import datetime

# Google Maps
# app.config['GOOGLEMAPS_KEY'] = "AIzaSyAGIOSFvvdnHopfkR2wYQ9NJK5ZMk1fafQ"
# GoogleMaps(app)


# Wrapper for render_template to always include whether user is authenticated
def render_template_auth(template, **template_vars):
    return render_template(
        template,
        authenticated=current_user.is_authenticated,
        **template_vars
    )

# Manager route
def checkAndRedirectManager():
    if current_user.has_role('manager'):
        return render_template_auth('manager/index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template_auth('not_found.html')


@app.route('/', methods=['GET', 'POST'])
@auth_required()
def index():
    checkAndRedirectManager()

    # form = CreateBookingForm()

    # if form.validate_on_submit():
    #     # HIRING SCOOTER LOGIC

    #     # EMAIL SENDING

    if current_user.has_role('manager'):
        return render_template_auth('manager/index.html')
           
    return render_template_auth('index.html')

    # return render_template_auth('index.html', form=allLocations)

@app.route('/account', methods=['GET'])
@auth_required()
def my_account():

    #for users to view their account details
    
    user_email = current_user.email

    user = models.User.query.filter_by(email=user_email).first()
    details = models.BankDetails.query.filter_by(id=user.bank_details_id).first()

    return render_template_auth('my_account.html', title = 'My Account', user=user, card_details=details)

@app.route('/account/bank_details', methods=['GET', 'POST'])
@auth_required()
def bank_details():

    #for users to store their bank details
    #userid = session.get('id')
    #user = models.User.query.filter_by(id=userid).first()
    
    #if request.method == 'POST':
    details_form = StoreCardDetailsForm()
    
    if details_form.validate_on_submit():
        details = models.BankDetails(
            name = details_form.name.data,
            accountNo = details_form.accountNo.data,
            sortCode = details_form.sortCode.data,
            expiry = details_form.expiry.data,
            cvc = details_form.cvc.data
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
 
    return render_template_auth('bank_details.html', title = 'My Account', form=details_form)

# Manager Page
@app.route('/manager')
@roles_required('manager')
@auth_required()
def manager():
    allLocations = models.Location.query.all()
    
    allScooters = models.Scooter.query.all()

    return render_template_auth('manager/index.html', locations=allLocations, Scooters=allScooters)

@app.route('/manager/add-location', methods=['GET', 'POST'])
@roles_required('manager')
@auth_required()
def managerAddLocation():
    form = LocationForm()

    if form.validate_on_submit():
        newLocation = models.Location(
            name = form.name.data,
            x_cord = form.x_cord.data,
            y_cord = form.y_cord.data
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

    scootersInLocation = models.Scooter.query.filter_by(location_id=location, availability=True).all()

    return json.jsonify({'scooters': models.Scooter.serialize_list(scootersInLocation)})

# Add a scooter to the location
@app.route('/api/addScooter')
def addScooterToLocation():
    locationId = request.args.get('locationId')

    newScooter = models.Scooter(
        location_id = locationId
    )

    db.session.add(newScooter)
    db.session.commit()

    return '200'

