import os
from flask import Flask

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    def serialize(self):
        return({
            'id': self.id,
            'team_id': self.team_id,
            'slack_id': self.slack_id,
            'display_name': self.display_name,
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

@app.route('/', methods=['GET', 'POST'])
def receive_data():
    if request.method == 'POST':
        data = request.get_json()

        if data["token"]:
            ret = '{"challenge":' + data["challenge"] + '}'

            response = Response(
                response = ret,
                status = 200,
                mimetype = 'application/json'
            )

            return response

        else:
            # Do some other stuff with the data received from the Event API
            return('Got some data!!')

    elif request.method == 'GET':
        return('Hello World!')