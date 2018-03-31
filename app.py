import os
from flask import Flask
from flask import jsonify
from flask import render_template

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .helpers import get_challenge_response

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

    reactions_sent = db.relationship('Reaction', primaryjoin="User.id==Reaction.user_id_rs", backref='sender', lazy=True)
    reactions_received = db.relationship('Reaction', primaryjoin="User.id==Reaction.user_id_rr", backref='receiver', lazy=True)

    def serialize(self):
        return({
            'id': self.id,
            'team_id': self.team_id,
            'slack_id': self.slack_id,
            'display_name': self.display_name,
            'reactions_sent': self.reactions_sent,
            'reactions_received': self.reactions_received
        })

class Reaction(Base):
    name = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text)
    
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    user_id_rs = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_rr = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def serialize(self):
        return({
            'id': self.id,
            'team_id': self.team_id,
            'date_created': self.date_created,
            'name': self.name,
            'sender_id': self.user_id_rs,
            'receiver_id': self.user_id_rr,
            'message': self.message
        })

class Channel(Base):
    slack_id = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    is_private = db.Column(db.Boolean)
    reaction_id = db.relationship('Reaction', primaryjoin="Channel.id==Reaction.channel_id", backref='channel', lazy=True)

    def serialize(self):
        return({
            'id': self.id,
            'slack_id': self.slack_id,
            'team_id': self.team_id,
            'name': self.name,
            'is_private': self.is_private
        })

app = Flask(__name__)
app.config.from_pyfile('instance/config.py')

with app.app_context():
    db.init_app(app)

migrations_directory = os.path.join('migrations')
migrate = Migrate(app, db, directory=migrations_directory)

## ROUTES

@app.route('/', methods=['GET', 'POST'])
def receive_data():
    if request.method == 'POST':
        data = request.get_json()

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
    data = request.form.to_dict()

    if data.get('type'):
        return(get_challenge_response(data, app.config['SLACK_VERIFICATION_TOKEN'])) 
    else:
        return(jsonify({ "text": "Test reply: " + data['text'] + " from " + data['user_name'] }))

@app.route('/api/slack/events', methods=['POST'])
def incoming_event():
    data = request.get_json()

    if data['type'] == 'url_verification':
        return(get_challenge_response(data, app.config['SLACK_VERIFICATION_TOKEN']))

    elif data['type'] == 'reaction_added':
        channel = ""

        if data['item']['type'] == 'message':
            channel_id = data['item']['channel']

        reaction = {
            'sender_id': data['user'],
            'receiver_id': data['item_user'],
            'channel_id': channel_id,
            'reaction': data['reaction']
        }

        return(jsonify(reaction))
