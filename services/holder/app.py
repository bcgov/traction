from flask import Flask, jsonify, abort, request, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
import logging 

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db) 

TOPICS = ['connections']

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/log/topic/<topic>/", methods=['POST'])
def acapy_event_handler(topic):
    app.logger.info(f'topic={topic}')
    app.logger.debug(request)

    if topic in TOPICS:
        app.logger.info(f"HANDLE {topic} event")
        event = Event(topic=topic, event_raw=str(request))
        db.session.add(event)
        db.session.commit()
    else:
        app.logger.info(f"IGNORE {topic} event")

    return make_response(jsonify({'success': True}), 200)


class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = { "schema": 'holder' }

    id = db.Column(db.Integer,primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    event_raw = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Event %r:%r>' % self.id, self.topic
        