import unittest
import random

from slackertracker.app import create_app, db
from slackertracker.app import Channel
from slackertracker.tests.suite import test_config

from slackertracker.factories.channel import generate_channel
from slackertracker.factories.user import generate_user
from slackertracker.factories.reaction import generate_reaction
from slackertracker.factories.utils import generate_id

class TestReactionModel(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        app.testing = True
        self.app = app.test_client()
        db.create_all()


    def test_create_valid_reaction(self):
        team_id = generate_id('T')

        user = generate_user(team_id=team_id)
        channel = generate_channel(team_id=team_id, is_private=False)

        db.session.add_all([user, channel])
        db.session.commit()

        reaction = generate_reaction(sender=user, channel=channel)
        db.session.add(reaction)
        db.session.commit()

    def test_many_valid_reactions(self):
        team_id = generate_id('T')

        users = [generate_user(team_id) for _ in range(0, 100)]
        channels = [generate_channel(team_id) for _ in range(0,5)]
        
        db.session.add_all(users)
        db.session.add_all(channels)
        db.session.commit()

        reactions = []

        for _ in range(0,1000):
            sender = random.choice(users)
            receiver = random.choice(users)
            channel = random.choice(channels)
            reactions.append(generate_reaction(sender=sender, channel=channel, receiver=receiver))

        db.session.add_all(reactions)
        db.session.commit()

        for reaction in reactions:
            self.assertIsNotNone(reaction.id)
            found_reaction = reaction.query.get(reaction.id)
            self.assertEqual(reaction.id, found_reaction.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        