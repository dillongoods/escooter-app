from flask import render_template, flash, request, session, redirect, db
from app import app, models
from .forms import RegistrationForm, LogIn, AddItem, ChangePassword, StoreCardDetails, CreateBooking

def signedIn():
    return session.get('loggedIn') == True

def unsignedIn():
    return session.get('loggedIn') is None or session.get('loggedIn') == False


@app.route('/')
def index():
    roles = models.Role.query.all()
    users = models.User.query.all()
    return ' '.join([role.name for role in roles])

@app.route('/log_in', methods=['GET', 'POST'])
def log_in():

    if signedIn() == True:
        #logging.info('User doesnt need to log in as theyre already logged in')
        return redirect('/')

    form = LogIn()
    if form.validate_on_submit():
        existingUser = models.User.query.filter_by(email=form.email.data).first()

        if existingUser is None:
            flash('%s is not registered in our database. Register first to continue'%(form.email.data))
            app.logger.info('%s failed to log in', form.email.data)
        elif existingUser.password != form.password.data:
            flash('Incorrect password')
            app.logger.info('%s failed to log in', existingUser.email)
        else:
            session['loggedIn'] = True
            session['id'] = existingUser.id
            session['email'] = existingUser.email
            app.logger.info('%s logged in successfully', existingUser.email)
            return redirect('/')

    return render_template('log_in.html', title='Log in', form=form)

@app.route('/logout')
def logout():
    session.pop('loggedIn', None)
    #logging.info('user logged out')
    return redirect('/')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePassword()

    if form.validate_on_submit():

        userid = session.get('id')
        user = models.User.query.filter_by(id=userid).first()

        if form.newPassword.data != form.repeatNew.data:
            flash("Passwords dont match, please try again")
        elif (user.password != form.oldPassword.data):
            #logging.basicConfig(format='%(asctime)s %(message)s')
            #logging.info(': failed change password attempt')
            flash("Old password doesn't match password on account")
        elif form.newPassword.data == form.repeatNew.data and user.password == form.oldPassword.data:
            user.password = form.newPassword.data
            db.session.commit()
            #app.logger.info('%s changed password', user.email)
            flash("Password changed successfully")

    return render_template('change_password.html', form=form)
