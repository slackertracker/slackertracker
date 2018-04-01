import unittest

from slackertracker.app import create_app, db
from slackertracker.app import Channel
from slackertracker.tests.suite import test_config

class TestChannelModel(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        app.testing = True
        self.app = app.test_client()
        db.create_all()


    def test_create_valid_channel(self):
        new_channel = Channel()
        new_channel.team_id = "A12341234"
        new_channel.slack_id = "C12341234"
        new_channel.name = "channel_name"
        db.session.add(new_channel)
        db.session.commit()

        found_channel = Channel.query.all()[0]

        self.assertEqual(found_channel.id, 1)
        self.assertEqual(found_channel.team_id, "A12341234")
        self.assertEqual(found_channel.slack_id, "C12341234")
        self.assertEqual(found_channel.name, "channel_name")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        