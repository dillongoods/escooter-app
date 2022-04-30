import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models, user_datastore


def setup_db():
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config.from_object('config')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    #the basedir lines could be added like the original db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    user_datastore.create_role(name="manager")
    user_datastore.create_role(name="employee")
    user_datastore.create_role(name="customer")

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

if __name__ == '__main__':
    unittest.main()