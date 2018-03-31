import unittest

from slackertracker.app import create_app, db
from slackertracker.app import User, Channel, Reaction

test_config = 'instance/test_config.py'

class TestHello(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()


    def test_hello(self):
        response = self.app.get('/')
        assert b'Hello!' in response.data

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestCreateUser(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        app.testing = True
        self.app = app.test_client()
        db.create_all()


    def test_valid(self):
        new_user = User()
        new_user.team_id = "A12341234"
        new_user.slack_id = "U12341234"
        new_user.display_name = "nathan"
        db.session.add(new_user)
        db.session.commit()

        found_user = User.query.all()[0]

        self.assertEqual(found_user.id, 1)
        self.assertEqual(found_user.team_id, "A12341234")
        self.assertEqual(found_user.slack_id, "U12341234")
        self.assertEqual(found_user.display_name, "nathan")

    def tearDown(self):
        db.session.remove()
        db.drop_all()