import os
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# helpers
from slackertracker.helpers import get_challenge_response
from slackertracker.helpers import get_user_by_slack_id
from slackertracker.helpers import get_channel_by_slack_id

# Stuff for routing
from flask import request
from flask import Response

## MODELS
db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class User(Base):
    team_id = db.Column(db.String(32), nullable=False)
    slack_id = db.Column(db.String(32), unique=True, nullable=False)
    display_name = db.Column(db.String(128), nullable=False)

    reactions_sent = db.relationship('Reaction', primaryjoin="User.id==Reaction.sender_id", backref='sender', lazy=True)
    reactions_received = db.relationship('Reaction', primaryjoin="User.id==Reaction.receiver_id", backref='receiver', lazy=True)

    def serialize(self):
        return({
            'id': self.id,
            'team_id': self.team_id,
            'slack_id': self.slack_id,
            'display_name': self.display_name,
            'reactions_sent': self.reactions_sent,
            'reactions_received': self.reactions_received
        })

@db.event.listens_for(User, "after_insert")
def user_created_debug(mapper, connection, user):
    """
    Prints debug info when a user is created.
    """
    if current_app.debug == True:
        print("New user: " + str(user.serialize()))

class Reaction(Base):
    name = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def serialize(self):
        return({
            'id': self.id,
            'team_id': self.team_id,
            'date_created': self.date_created,
            'name': self.name,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'channel_id': self.channel_id
        })

@db.event.listens_for(Reaction, "after_insert")
def reaction_created_debug(mapper, connection, reaction):
    """
    Prints debug info when a reaction is created.
    """
    if current_app.debug == True:
        print("New reaction: " + str(reaction.serialize()))

class Channel(Base):
    slack_id = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(32))
    is_private = db.Column(db.Boolean)
    reactions = db.relationship('Reaction', primaryjoin="Channel.id==Reaction.channel_id", backref='channel', lazy=True)

    def serialize(self):
        return({
            'id': self.id,
            'slack_id': self.slack_id,
            'team_id': self.team_id,
            'name': self.name,
            'is_private': self.is_private,
            'reactions': self.reactions,
        })

@db.event.listens_for(Channel, "after_insert")
def channel_created_debug(mapper, connection, channel):
    """
    Prints debug info when a channel is created.
    """
    if current_app.debug == True:
        print("New channel: " + str(channel.serialize()))

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    with app.app_context():
        db.init_app(app)

    migrations_directory = os.path.join('migrations')
    migrate = Migrate(app, db, directory=migrations_directory)

    ## ROUTES

    @app.route('/', methods=['GET', 'POST'])
    def receive_data():
        if request.method == 'POST':
            data = request.get_json()
            if app.debug:
                print('/ POST data: ', data)

            if data['type'] == 'url_verification':
                return(get_challenge_response(data, app.config['SLACK_VERIFICATION_TOKEN']))

            else:
                # Do some other stuff with the data received from the Event API
                return(jsonify(data))

        elif request.method == 'GET':
            return("Hello!")

    @app.route('/auth/request')
    def auth_request():
        return render_template('add_to_slack.html')

    @app.route('/auth/granted')
    def auth_granted():
        return("Authorized.")

    @app.route('/api/slack/commands', methods=['POST'])
    def slash_command():
        data = request.form.to_dict() or request.get_json()
        if app.debug:
            print('/api/slack/commands POST data: ', data)

        if data.get('type'):
            return(get_challenge_response(data))
        else:
            # /api/slack/commands with no params - give top 5 received emojis for current user
            user_name = data.get('user_name')
            slack_user_id = data.get('user_id')
            req_text = data.get('text')
            if req_text.strip() == '':
                if app.debug:
                    print('{} requested top 5 emojis received by self'.format(user_name))
                
                user = User.query.filter_by(slack_id=slack_user_id).first()
                reaction_counts = {}
                if user:
                    for reaction in user.reactions_received:
                        reaction_counts[reaction.name] = reaction_counts.get(reaction.name, 0) + 1

                sorted_reactions = sorted(reaction_counts, key=reaction_counts.get, reverse=True)
                resp_text = "Top 5 Emojis Received By {}\n".format(user_name)
                for reaction in sorted_reactions[:5]:
                    resp_text += ":{}: : {}\n".format(reaction, str(reaction_counts[reaction]))
                if not sorted_reactions:
                    resp_text += "You don't have any reactions. :cry:\n" 
                return(jsonify({ "text": resp_text }))

            # default test resp
            else:
                if app.debug:
                    print('{} requested test reply'.format(user_name))
                return(jsonify({ "text": "Test reply: {} from {}".format(req_text, user_name) })) 
       
    @app.route('/api/slack/events', methods=['POST'])
    def incoming_event():
        data = request.get_json()
        if app.debug:
            print('/api/slack/events POST data: ', data)

        if data.get('type') == 'url_verification':
            return(get_challenge_response(data))

        elif data.get('type') == 'event_callback':
            event = data.get('event')
            item = event.get('item')
            team_id = data.get('team_id')

            sender_slack_id = event.get('user')
            sender = User.query.filter_by(slack_id=sender_slack_id).first()
            if sender is None:
                user_data = get_user_by_slack_id(sender_slack_id)

                sender = User(
                    display_name = user_data.get('display_name'),
                    slack_id = sender_slack_id,
                    team_id = team_id
                )

                db.session.add(sender)
                db.session.commit()
                sender = User.query.filter_by(slack_id=sender_slack_id).first()
            
            receiver_slack_id = event.get('item_user')
            if receiver_slack_id:
                receiver = User.query.filter_by(slack_id=receiver_slack_id).first()
                if receiver is None:
                     user_data = get_user_by_slack_id(receiver_slack_id)
                     receiver = User(
                         slack_id = receiver_slack_id,
                         display_name = user_data.get('display_name'),
                         team_id = team_id
                     )
                     db.session.add(receiver)
                     db.session.commit()
            
            if item.get('type') == 'message':
                channel_id = item.get('channel')
                channel = Channel.query.filter_by(slack_id=channel_id).first()

                if not channel:
                    channel_data = get_channel_by_slack_id(channel_id)
                    channel = Channel(
                        slack_id = channel_id,
                        team_id = team_id,
                        name = channel_data.get('name'),
                        is_private = channel_data.get('is_private')
                    )
                    db.session.add(channel)
                    db.session.commit()
                    channel = Channel.query.filter_by(slack_id=channel_id).first()

            reaction = Reaction(
                name = event.get('reaction'),
                team_id = team_id,
                sender_id = sender.id,
                receiver_id = receiver.id if receiver_slack_id else None,
                channel_id = channel.id
            )

            db.session.add(reaction)
            db.session.commit()

            return(jsonify(reaction.serialize()))

    return(app)
