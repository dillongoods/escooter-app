from flask import session, render_template
from app import app, models, db
from flask_security import login_required, current_user

# Wrapper for render_template to always include whether user is authenticated
def render_template_auth(template, **template_vars):
    return render_template(
        template, 
        authenticated = current_user.is_authenticated,
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
    return render_template_auth('index.html', roles = roles, users = users)
