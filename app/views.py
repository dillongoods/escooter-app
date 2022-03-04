from flask import session, render_template, request, redirect
from app import app, models, db
from flask_security import login_required, current_user
from .forms import StoreCardDetailsForm
import datetime


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


@app.route('/')
def index():
    # return render_template_auth('index.html')

    roles = models.Role.query.all()
    users = models.User.query.all()
    bank_details = models.BankDetails.query.all()
    return render_template_auth('index.html', roles=roles, users=users, bank_details=bank_details)

# @app.route('/')
# def index():
#     # return render_template_auth('index.html')

#     roles = models.Role.query.all()
#     users = models.User.query.all()
#     return render_template_auth('index.html', roles=roles, users=users)


@app.route('/account', methods=['GET'])
def my_account():

    #for users to view their account details
    
    user_id = current_user.id

    user = models.User.query.filter_by(id=user_id).first()
    details = models.BankDetails.query.filter_by(id=user.bank_details_id).first()
    
    # details = {
    #     "id":1,
    #     "name":"MR BUSHNELL",
    #     "accountNo":12034283234,
    #     "expiry": datetime.datetime.now().date(),
    #     "sortCode":2113,
    #     "cvc":666,
    # }

    return render_template_auth('my_account.html', title = 'My Account', email=current_user.email, card_details=details)

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
