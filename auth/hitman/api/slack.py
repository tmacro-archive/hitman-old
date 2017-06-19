from flask import Blueprint, request, url_for, session, jsonify
from ..app import db
from ..models import User
from ..util.config import config
from ..util.log import getLogger
from ..util.crypto import check_token, expiring_token
from ..util.storage import create_user, from_slack
import requests

_log = getLogger('api.slack')

slack_app = Blueprint('slack', __name__)

@slack_app.route('/authorize', methods = ['POST'])
def authorize():
	data = request.args
	if not data or not data.get('slack'):
		return '501' # Malformed request
	slack_user = data.get('slack')
	user = from_slack(slack_user)
	if not user:
		user = create_user(slack = slack_user)
	if user and user.confirmed:
		return jsonify(dict(success = True, uid = user.uid, url = None))
	reg_token = expiring_token(user.secret, user.key)
	reg_url = url_for('auth.landing', user = slack_user, token = reg_token, _external = True)
	return jsonify(dict(success = True, url = reg_url, uid = None))

def slack_authorized(slack, uid):
	resp = requests.post(config.api.gygax, params = dict(user=slack,uid=uid, valid=True))
	return resp.status_code == 200
