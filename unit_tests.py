import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models, user_datastore, views, setup
from flask_security.utils import hash_password

def app_context():
    with app.app_context():
        yield

def setup_db():
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config.from_object('config')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    #the basedir lines could be added like the original db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')

    user_datastore.create_role(name="manager")
    user_datastore.create_role(name="employee")

    db.create_all()

def teardown_db():
    db.session.remove()
    db.drop_all()
class TestRoutes(unittest.TestCase):
    def setUp(self):
        setup_db()
        self.app = app.test_client()
        pass

    def tearDown(self):
        teardown_db()

    def test_homeroute(self):
        response = self.app.get('/',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Unable to locate home route '/'")

class TestDatabase(unittest.TestCase):
    def setUp(self):
        setup_db()
        self.app = app.test_client()
        pass

    def tearDown(self):
        teardown_db()


    def test_add_user(self):
        user_datastore.create_user(email='test@test.net', password='password', roles=['manager'])
        
        try:
            db.session.commit()
            # Passed
            self.assertTrue(True)
        except:
            # Failed
            self.assertTrue(False, "Unable to add user to db.")


    def test_password_encrypted(self):
        password = 'testingpassword123'
        email = 'test@password.com'
        with app.app_context():
            user_datastore.create_user(first_name='test', last_name='password', email=email, password=hash_password(password))

            db.session.commit()

            # user_datastore.find_user(email=email)
            user = models.User.query.filter_by(email=email).first()

        self.assertNotEqual(user.password, password, "Password is not encrypted.")



    # test roles added
    def test_roles_added(self):
        self.assertTrue(user_datastore.find_role("manager"), "No manager role.")
        self.assertTrue(user_datastore.find_role("employee"), "No employee role.")


    # test scooters exist
    def test_scooters_exist(self):
        setup.add_locations()
        setup.add_scooters()

        scooters = models.Scooter.query.all()
        self.assertEqual(len(scooters), 20, f"There should be 20 scooters in the database but found {len(scooters)}.")

        pass


    # test scooter locations exist
    def test_locations_exist(self):
        setup.add_locations()

        locations = models.Location.query.all()
        
        self.assertEqual(len(locations), 5, f"There should be 5 locations in the database but found {len(locations)}.")
        pass


if __name__ == '__main__':
    unittest.main()