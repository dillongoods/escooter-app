from app import app, models

@app.route('/')
def index():
    roles = models.Role.query.all()
    users = models.User.query.all()
    return ' '.join([role.name for role in roles])