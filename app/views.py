from flask import session, render_template, request, redirect, flash
from app import app, models, db
from flask_security import login_required, current_user, logout_user
from .forms import StoreCardDetailsForm, CreateBookingForm
import datetime
from flask_mail import Mail, Message

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '97e041d5e367c7'
app.config['MAIL_PASSWORD'] = 'cfaf5b99f8bafb'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

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

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        form = CreateBookingForm()

        if form.validate_on_submit():
            # HIRING SCOOTER LOGIC

            # EMAIL SENDING
            msg = Message('Booking confirmation', sender = 'scooterz@mailtrap.io', recipients = [current_user.email])
            msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
            mail.send(msg)
            return render_template_auth('index.html', form=form)

        return render_template_auth('index.html', form=form)

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
