import unittest

from slackertracker.app import create_app, db
from slackertracker.app import User
from slackertracker.tests.suite import test_config
from slackertracker.factories.user import generate_user
from slackertracker.factories.utils import generate_id

class TestUserModel(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        app.testing = True
        self.app = app.test_client()
        db.create_all()


    def test_create_valid_user(self):
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

    def test_create_ten_users(self):
        team_id = generate_id('T')
        users = [generate_user(team_id) for _ in range(0, 10)]
        db.session.add_all(users)
        db.session.commit()

        for user in users:
            self.assertIsNotNone(user.id)
            found_user = User.query.get(user.id)
            self.assertEqual(user.id, found_user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        