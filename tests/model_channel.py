import unittest

from slackertracker.app import create_app, db
from slackertracker.app import Channel
from slackertracker.tests.suite import test_config
from slackertracker.factories.channel import generate_channel
from slackertracker.factories.utils import generate_id

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

    def test_create_ten_channels(self):
        team_id = generate_id('T')
        channels = [generate_channel(team_id) for _ in range(0, 10)]
        db.session.add_all(channels)
        db.session.commit()

        for channel in channels:
            self.assertIsNotNone(channel.id)
            found_channel = channel.query.get(channel.id)
            self.assertEqual(channel.id, found_channel.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        