import os
from flask import Flask

from flask import jsonify
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

class Reaction(Base):
    name = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text)
    
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

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
            'message': self.message
        })

class Channel(Base):
    slack_id = db.Column(db.String(32), nullable=False)
    team_id = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    is_private = db.Column(db.Boolean)
    reactions = db.relationship('Reaction', primaryjoin="Channel.id==Reaction.channel_id", backref='channel', lazy=True)

    def serialize(self):
        return({
            'id': self.id,
            'slack_id': self.slack_id,
            'team_id': self.team_id,
            'name': self.name,
            'is_private': self.is_private,
            'reactions': self.reactions
        })

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

with app.app_context():
    db.init_app(app)

migrations_directory = os.path.join('migrations')
migrate = Migrate(app, db, directory=migrations_directory)

## ROUTES

@app.route("/user")
def show_users():
    user = User.query.all()[0]
    return jsonify(user.serialize())

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/', methods=['GET', 'POST'])
def receive_data():
    if request.method == 'POST':
        data = request.get_json()

        if data['type'] == 'url_verification':
            return(get_challenge_response(data))

        else:
            # Do some other stuff with the data received from the Event API
            return(data)

    elif request.method == 'GET':
        return('Hello World!')

@app.route('/api/slack/commands', methods=['POST'])
def slash_command():
    data = request.get_json()

    if data['type'] == 'url_verification':
        return(get_challenge_response(data)) 

    else:
        return(data)

@app.route('/api/slack/events', methods=['POST'])
def incoming_event():
    data = request.get_json()

    if data['type'] == 'url_verification':
        return(get_challenge_response(data))

    else:
        return data
