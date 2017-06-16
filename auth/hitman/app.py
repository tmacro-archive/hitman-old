from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from .util.config import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.secret_key = config.crypto.key
app.config['SERVER_NAME'] = config.http.name

# create Database
db = SQLAlchemy(app)
oauth = OAuth(app)

from .api.auth import auth_app
app.register_blueprint(auth_app, url_prefix = '/auth')

from .api.slack import slack_app
app.register_blueprint(slack_app, url_prefix = '/slack')

