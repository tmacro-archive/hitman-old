from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .util.config import config
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hitman.db'
app.secret_key = config.crypto.server
app.config['SERVER_NAME'] = config.http.name

# Create database
db = SQLAlchemy(app)

from .bot.agent import Agent
from .api.slack import Slack

agent = Agent()
agent.start()

slack = Slack(agent.put)
