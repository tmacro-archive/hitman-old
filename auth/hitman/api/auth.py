import json
import requests
from flask import Blueprint, request, url_for, session, redirect
from ..app import db, oauth
from ..util.tmpl import templated
from ..util.session import UserSession
from ..util.config import config
from ..util.log import getLogger
from ..util.storage import from_slack, link_intra
from ..util.crypto import check_token
from .slack import slack_authorized
_log = getLogger('auth')

auth_app = Blueprint('auth', __name__)

oauth42 = oauth.remote_app('42',
	base_url = 'https://api.intra.42.fr',
	authorize_url='https://api.intra.42.fr/oauth/authorize',
	access_token_url="https://api.intra.42.fr/oauth/token",
	consumer_key = config.oauth.key,
	consumer_secret = config.oauth.secret
)

def get_arg(request, key):
	return request.args.get(key)

def get_uid(ft_token):
	headers = dict(Authorization = 'Bearer %s'%ft_token)
	resp = requests.get(config.api42.base + config.api42.info, headers = headers)
	if resp.status_code == 200:
		return resp.json().get('login')


@auth_app.route('/landing')
@templated('error.html')
def landing():
	'''
		This endpoint collects the slack user, and auth token from the request
		checks them for validity,
		checks if the slack user needs authentication
		redirects to /authenticate if needed
	'''
	__log = _log.getChild('landing')
	slack = get_arg(request, 'user')
	token = get_arg(request, 'token')
	if not slack and not token: # these should always be here
		__log.debug('Not enough info provided in request')
		return dict(content=config.content.no_token, title='Uh Oh?!')
	user = from_slack(slack)
	if not user or not check_token(user.secret, user.key, token):
		__log.debug('Invalid validation token')
		return dict(content=config.content.no_token, title='Uh Oh?!')
	if user.confirmed:
		__log.debug('User is already confirmed')
		return dict(content=config.content.already_registered, title='What did you want me to do?')
	__log.debug('Slack user %s is a candidate for registration, redirecting to /authenticate'%slack)
	auth_sess = UserSession()
	auth_sess.slack = slack
	auth_sess.token = token
	auth_sess.validate()
	session['auth'] = auth_sess.data
	return redirect(url_for('auth.authenticate'))

@auth_app.route('/authenticate')
def authenticate():
	__log = _log.getChild('authenticate')
	auth_sess = UserSession(**session.get('auth', {}))
	if not auth_sess.valid:
		__log.debug('User session is not valid redirecting to /landing')
		return redirect(url_for('auth.landing') )
	__log.debug('Redirecting request to 42 oauth endpoint')
	return oauth42.authorize(callback=url_for('auth.authorized', _external = True))

@auth_app.route('/authorized')
def authorized():
	__log = _log.getChild('authorized')
	__log.debug('Got redirect from 42 intra')
	auth_sess = UserSession(**session.get('auth', {}))	
	resp = oauth42.authorized_response()
	if resp is None or not auth_sess.valid:
		_log.debug('User has refused our access request')
		return redirect(url_for('auth.landing'))
	_log.debug('User has granted our access request')
	token = resp['access_token']
	refresh = resp['refresh_token']
	uid = get_uid(token)
	link_intra(auth_sess.slack, uid, token, refresh)
	slack_authorized(auth_sess.slack, uid)
	auth_sess.uid = uid
	session['auth'] = auth_sess.data
	return redirect(url_for('auth.complete'))

@auth_app.route('/complete')
@templated('complete.html')
def complete():
	auth_sess = UserSession(**session.get('auth', {}))
	if not auth_sess.valid:
		return redirect(url_for('auth.landing'))
	return dict(user=auth_sess.uid)