from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from hitman.util.config import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hitman.db'
app.secret_key = config.crypto.key
app.config['SERVER_NAME'] = config.http.name
# create Database
db = SQLAlchemy(app)
oauth = OAuth(app)

from hitman.api.auth import auth_app

app.register_blueprint(auth_app)