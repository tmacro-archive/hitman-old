from flask import Blueprint, request, url_for, session, jsonify
from ..app import db
from ..models import User
from ..util.config import config
from ..util.log import getLogger
from ..util.crypto import check_token, expiring_token

_log = getLogger('api.slack')

slack_app = Blueprint('slack', __name__)

@slack_app.route('/register', methods = ['POST'])
def register():
	data = request.args
	if not data or not data.get('slack'):
		return '501' # Malformed request
	slack_user = data.get('slack')
	user = User.from_slack(slack_user)
	if user:
		return jsonify(dict(success = False, error = 'Already Registered'))
	user = User(slack = slack_user)
	db.session.add(user)
	db.session.commit()
	reg_token = expiring_token(user.secret, user.key)
	reg_url = url_for('auth.register', user = slack_user, token = reg_token, _external = True)
	return jsonify(dict(success = True, url = reg_url))

