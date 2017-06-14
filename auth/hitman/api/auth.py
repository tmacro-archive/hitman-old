import json
from flask import Blueprint, request, url_for, session
import requests
from ..models import User, Weapon, Location
from ..app import db
from .oauth import oauth42
auth_app = Blueprint('auth', __name__)
from ..util.config import config
from ..util.log import getLogger

_log = getLogger('api.auth')

@oauth42.tokengetter
def get_42oauth_token(token=None):
    return session.get('42_oauth_token')

@auth_app.route("/register")
def register():
	return oauth42.authorize(callback=config.oauth.callback)

@auth_app.route("/oauth_authorized")
def authorized():
	resp = oauth42.authorized_response()
	if resp is None:
		return 'false'
	token = resp['access_token']
	refresh = resp['refresh_token']
	session['42_oauth_token'] = (token, refresh)
	headers = dict(Authorization = 'Bearer %s'%token)
	resp = requests.get(config.api42.base + '/v2/me', headers = headers)
	if resp.status_code == 200:
		login = resp.json().get('login')
		u = User.query.filter_by(uid = login).first()
		if not u:
			_log.debug('user %s not found, creating...'%login)
			u = User(login)
			db.session.add(u)
			db.session.commit()
	return 'true'