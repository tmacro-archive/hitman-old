import json
import requests
from flask import Blueprint, request, url_for, session, redirect
from ..app import db, oauth
from ..util.config import config
from ..util.log import getLogger
from ..util.crypto import check_token
from ..util.tmpl import templated
from ..models import User

_log = getLogger('api.auth')

auth_app = Blueprint('auth', __name__)

oauth42 = oauth.remote_app('42',
	base_url = 'https://api.intra.42.fr',
	authorize_url='https://api.intra.42.fr/oauth/authorize',
	access_token_url="https://api.intra.42.fr/oauth/token",
	consumer_key = config.oauth.key,
	consumer_secret = config.oauth.secret
)

@oauth42.tokengetter
def get_42oauth_token(token=None):
    return session.get('42_oauth_token')

@auth_app.route("/register")
@templated('landing.html')
def register():
	_llog = _log.getChild('auth.register')
	slack_user = request.args.get('user') if request.args.get('user') else session.get('slack_user')
	slack_token = request.args.get('token') if request.args.get('token') else session.get('slack_token')
	ft_user = User.from_slack(slack_user)
	ft_token, ft_refresh = session.get('ft_oauth_token', (False, False))
	if not slack_token or not ft_user or not ft_user:
		_llog.debug('Request does not contain sufficient info, user arrived to early')
		return dict(content=config.content.no_token, title="Uh Oh!?") # redirect to explanation about slack signup
	session['slack_user'] = slack_user
	session['slack_token'] = slack_token
	if not ft_token: # redirect to 42 oauth page
		_llog.debug('User has not logged into 42 yet, redirecting...')
		# return oauth42.authorize(callback=url_for('auth.authorized', _external = True))
		return None
	if not check_token(ft_user.secret, ft_user.key, slack_token):
		_llog.debug('slack_token is invalid?? redirecting to "signup page"')
		return dict(content=config.content.no_token) # redirect to explanation about slack signup
	if ft_user.uid:
		_llog.debug('user has already registered')
		return '503' # user already registered
	_llog.debug('slack user authenticated, requesting intra info')
	headers = dict(Authorization = 'Bearer %s'%ft_token)
	resp = requests.get(config.api42.base + config.api42.info, headers = headers)
	if resp.status_code == 200:
		ft_user.uid = resp.json().get('login')
		ft_user.ft_oauth_key = ft_token
		ft_user.ft_oauth_refresh = ft_refresh
		ft_user.slack_confirmed = True
		db.session.add(ft_user)
		db.session.commit()
		_llog.debug('associated intra: %s with slack: %s'%(ft_user.uid, ft_user.slack))
	else:
		_llog.error('Error communicating with intra status: %s error')
	# Trigger successful registration slack message
	return '200' # redirect to success page

@auth_app.route("/oauth_authorized")
def authorized():
	_llog = _log.getChild('auth.authorized')
	resp = oauth42.authorized_response()
	if resp is None:
		_llog.debug('user has refused our access request')
		return 'false'
	_llog.debug('user has granted our access request')
	token = resp['access_token']
	refresh = resp['refresh_token']
	session['ft_oauth_token'] = (token, refresh)
	headers = dict(Authorization = 'Bearer %s'%token)
	resp = requests.get(config.api42.base + '/v2/me', headers = headers)
	return redirect(url_for('auth.register'))