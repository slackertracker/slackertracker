import unittest
import random

from flask import current_app

from sqlalchemy import func

from slackertracker.app import create_app, db
from slackertracker.app import Channel, User, Reaction
from slackertracker.tests.suite import test_config

from slackertracker.factories.channel import generate_channel
from slackertracker.factories.user import generate_user
from slackertracker.factories.reaction import generate_reaction
from slackertracker.factories.utils import generate_id

def add_users(count, team_id):
    users = [generate_user(team_id) for _ in range(0, count)]

    db.session.add_all(users)
    db.session.commit()
    return users

def add_channels(count, team_id):
    channels = [generate_channel(team_id, is_private=False) for _ in range(0, count)]

    db.session.add_all(channels)
    db.session.commit()
    return channels

def add_reactions_to_user(count, user, users, channels, team_id):
    reactions = []

    for _ in range(0, count):
        sender = random.choice(users)
        receiver = user
        channel = random.choice(channels)

        reaction = generate_reaction(sender, channel, receiver, team_id)
        reactions.append(reaction)

    db.session.add_all(reactions)
    db.session.commit()
    return reactions


# from https://gist.github.com/hest/8798884
def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count

class TestRouteCommands(unittest.TestCase):
    def setUp(self):
        # TODO: app.debug doesn't work in here
        app = create_app(test_config)
        app.testing = True
        self.app = app
        db.create_all()

    def test_api_slack_commands_exists(self):
        # TODO: fix route to handle missing data
        with current_app.test_client() as c:
            data = {
                'text': '',
                'user_name': 'bad_user',
                }
            response = c.post('/api/slack/commands', data=data)
            self.assertEquals(response.status_code, 200)

    def test_one_user_one_reaction(self):
        team_id = generate_id("T")

        receiver = generate_user(team_id=team_id)
        sender = generate_user(team_id=team_id)
        channel = generate_channel(team_id=team_id)
        db.session.add_all([receiver, sender, channel])

        db.session.commit()

        # check that count of reactions received is 0 before
        query = Reaction.query.filter_by(receiver_id=receiver.id)
        self.assertEqual(get_count(query), 0)

        reaction = generate_reaction(sender, channel, receiver, team_id=team_id)
        db.session.add(reaction)
        db.session.commit()

        # check count of reactions receiverd  is 1 after
        query = Reaction.query.filter_by(receiver_id=receiver.id)
        self.assertEqual(get_count(query), 1)

        data = {
            'user_id': receiver.slack_id,
            'text': '',
            'team_id': team_id,
            'token': current_app.config.get('SLACK_VERIFICATION_TOKEN'),
            'user_name': receiver.display_name,
        }

        with current_app.test_client() as c:
            response = c.post('/api/slack/commands', data=data)

            line = bytes(receiver.display_name, 'utf-8')
            self.assertIn(line, response.data)
            line = bytes(":{}: : {}".format(receiver.reactions_received[0].name, 1), 'utf-8')
            self.assertIn(line,response.data)
    
    def test_one_user_many_reactions(self):
        team_id = generate_id("T")
        users = add_users(5, team_id)
        receiver = users[0]
        channel = add_channels(1, team_id)[0]

        query = Reaction.query.filter_by(receiver_id=receiver.id)
        self.assertEqual(get_count(query), 0)

        reactions = []

        for i in range(0, 6):
            count = 10 - i
            for _ in range(0, count):
                sender = random.choice(users)
                reaction = generate_reaction(sender, channel, receiver, team_id)
                reaction.name = "test{}".format(i)
                reactions.append(reaction)

        db.session.add_all(reactions)
        db.session.commit()

        query = Reaction.query.filter_by(receiver_id=receiver.id)
        self.assertEqual(get_count(query), 45)

        data = {
            'user_id': receiver.slack_id,
            'text': '',
            'team_id': team_id,
            'token': current_app.config.get('SLACK_VERIFICATION_TOKEN'),
            'user_name': receiver.display_name,
        }

        with current_app.test_client() as c:
            response = c.post('/api/slack/commands', data=data)

            line = bytes(receiver.display_name, 'utf-8')
            self.assertIn(line, response.data)

            line = bytes(":{}: : {}".format("test0", 10), 'utf-8')
            self.assertIn(line,response.data)
            line = bytes(":{}: : {}".format("test1", 9), 'utf-8')
            self.assertIn(line,response.data)
            line = bytes(":{}: : {}".format("test2", 8), 'utf-8')
            self.assertIn(line,response.data)
            line = bytes(":{}: : {}".format("test3", 7), 'utf-8')
            self.assertIn(line,response.data)
            line = bytes(":{}: : {}".format("test4", 6), 'utf-8')
            self.assertIn(line,response.data)
            line = b'test5'
            self.assertNotIn(line,response.data)

    def tearDown(self):
        db.session.remove()
        db.drop_all()