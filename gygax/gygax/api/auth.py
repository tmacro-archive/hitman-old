import json
import requests
from ..util.config import config
from ..util.log import getLogger
from ..util.http import http
from ..app import agent
from ..bot.events import SlackValidationEvent
_log = getLogger('api.auth')

def validate_user(slack):
	_log.debug('Obtaining validation url for %s'%slack)
	resp = requests.post(config.api.auth.validate,
						params = dict(slack=slack))
	url = resp.json().get('url') if resp.json() else None
	if resp.status_code == 200 and url:
		_log.debug('Successfully got validation url for %s'%slack)
		return url
	_log.error('Failed to obtain validation url for %s'%slack)
	return None

@http.route('/slack_authorized', methods = ['POST'], params = True)
def _callback(data = None, params = None):
	_log.debug('Recieved notification of slack validation')
	if params:
		data = dict(
			user = params.get('user'),
			valid = params.get('valid'),
			uid = params.get('uid'),
			failed = not params.get('valid')
		)
		if data['user'] and (not data['valid'] or data['uid']):
			ev = SlackValidationEvent('user_validate', data)
			agent.proxy.put(ev)
			_log.debug('Recieved slack validation for user %s 42 uid %s'%(ev.user, ev.uid))
			return
	_log.warning('Malformed request from authentication server')