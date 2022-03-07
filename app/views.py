from flask import session, render_template, request, redirect, flash, json
from app import app, models, db
from flask_security import login_required, current_user, logout_user
from .forms import StoreCardDetailsForm, CreateBookingForm, LocationForm
# from flask_googlemaps import GoogleMaps, Map
import datetime

# Google Maps
# app.config['GOOGLEMAPS_KEY'] = "AIzaSyAGIOSFvvdnHopfkR2wYQ9NJK5ZMk1fafQ"
# GoogleMaps(app)


MANAGER_EMAIL = 'adminadmin321@gmail.com'

# Wrapper for render_template to always include whether user is authenticated
def render_template_auth(template, **template_vars):
    return render_template(
        template,
        authenticated=current_user.is_authenticated,
        **template_vars
    )

# Manager route
def checkAndRedirectManager():
    if current_user.email == MANAGER_EMAIL:
        return redirect('/manager')

@app.errorhandler(404)
def page_not_found(e):
    return render_template_auth('not_found.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.email == MANAGER_EMAIL:
        return redirect('/manager')

    if current_user.is_authenticated:
        # form = CreateBookingForm()

        # if form.validate_on_submit():
        #     # HIRING SCOOTER LOGIC

        #     # EMAIL SENDING
           
        return render_template_auth('index.html')

        # return render_template_auth('index.html', form=allLocations)

    return redirect('/login')

# @app.route('/')
# def index():
#     # return render_template_auth('index.html')

#     roles = models.Role.query.all()
#     users = models.User.query.all()
#     return render_template_auth('index.html', roles=roles, users=users)


@app.route('/account', methods=['GET'])
def my_account():

    #for users to view their account details
    
    user_email = current_user.email

    user = models.User.query.filter_by(email=user_email).first()
    details = models.BankDetails.query.filter_by(id=user.bank_details_id).first()
    
    # details = {
    #     "id":1,
    #     "name":"MR BUSHNELL",
    #     "accountNo":12034283234,
    #     "expiry": datetime.datetime.now().date(),
    #     "sortCode":2113,
    #     "cvc":666,
    # }

    return render_template_auth('my_account.html', title = 'My Account', user=user, card_details=details)

@app.route('/account/bank_details', methods=['GET', 'POST'])
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
def manager():
    allLocations = models.Location.query.all()
    
    allScooters = models.Scooter.query.all()

    return render_template_auth('manager/index.html', locations=allLocations, Scooters=allScooters)

@app.route('/manager/add-location', methods=['GET', 'POST'])
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

# API

@app.route('/api/getLocations')
def getLocations():
    allLocations = models.Location.query.all()
    
    return json.jsonify({'locations': models.Location.serialize_list(allLocations)})

@app.route('/api/getScooters')
def getScooters():
    
    allScooters = models.Scooter.query.all()
    
    return json.jsonify({'scooters', models.Scooter.serialize_list(allScooters)})