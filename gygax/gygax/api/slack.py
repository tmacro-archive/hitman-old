from ..util.pubsub import Subscriber
# from .storage import slack_id_to_slack
from ..util.config import config
from ..util.log import getLogger
from ..bot.events import MessageEvent, CommandEvent
import requests
_log = getLogger('api.slack')

auth_token = config.crypto.slack
default_data = dict(token=auth_token)

def build_url(ext):
	return config.apiSlack.base + ext

def reqOk(resp):
	if resp.json() and resp.json().get('ok'):
		return True
	return False

class Slack:
	def __init__(self, events):
		self._events = events
		self._user_map = {}
		self._subscriber = Subscriber(config.firehose.uri)

	def start(self):
		self._subscriber.open()
		self._setup_handlers()
	
	def stop(self):
		self._subscriber._close()

	def _uid_to_slack(uid):
		# slack = self._user_map.get(uid)
		slack = 'test'
		if not slack:
			slack = slack_id_to_slack(uid)
		return slack

	def _message_handler(self, msg):
		ev = MessageEvent(None, dict(user=msg['user'],text=msg['text'], channel=msg['channel']))
		_log.debug('Recieved message from %s'%ev.user)
		return self._events(ev)
	
	def _command_handler(self, msg):
		ev = CommandEvent('cmd_raw', dict(user = msg['user'], text=msg['text'], channel=msg['channel']))
		_log.debug('Recieved command %s'%ev.cmd)
		return self._events(ev)

	def _setup_handlers(self):
		self._subscriber.addHandler('msg', self._message_handler, strict = False)
		self._subscriber.addHandler('cmd', self._command_handler, strict = False)

	@staticmethod
	def _get_dms():
		resp = requests.post(build_url(config.apiSlack.dm_list),
							data = default_data)
		if resp.json().get('ok'):
			return resp.json().get('ims')

	@staticmethod
	def _get_dm_user(user):
		for dm in Slack._get_dms():
			if dm['user'] == user:
				return dm['id']
				
	@staticmethod
	def _get_user_info(user):
		data = dict(user=user)
		data.update(default_data)
		resp = requests.post(build_url(config.apiSlack.user_info),
							data = data)
		if resp.json() and resp.json().get('ok'):
			return resp.json().get('user')
		return None

	@staticmethod
	def _get_user_id(user):
		resp = requests.post(build_url(config.apiSlack.user_list),
							data = default_data)
		if resp.json().get('ok'):
			users = resp.json().get('members')
			for u in users:
				if u['name'] == user:
					return u['id']
	
	def _is_dm(self, channel):
		if channel in self._user_map:
			return True
		for ch in Slack._get_dms():
			if ch['id'] == channel:
				return True
		return False

	@staticmethod
	def _create_dm(user):
		data = dict(user=user)
		data.update(default_data)
		resp = requests.post(build_url(config.apiSlack.dm_new),
							data = data)
		if reqOk(resp):
			return resp.json().get('channel', {}).get('id')
		return None

	@staticmethod
	def _send_message(channel, message):
		data = dict(channel = channel, text = message)
		data.update(default_data)
		resp = requests.post(build_url(config.apiSlack.post_msg),
							data = data)
		if reqOk(resp):
			return True
		return False
	
	def msg(self, channel, message):
		return Slack._send_message(channel, message)

	def dm(self, user_id, message, cached = True):
		dm = self._user_map.get(user_id)
		if not dm:
			cached = False
			dm = Slack._get_dm_user(user_id)
		if not dm:
			dm = Slack._create_dm(user_id)
		if not dm:
			raise Exception('could not create direct message.')
		if not Slack._send_message(dm, message):
			if cached:
				self._user_map.pop(user_id)
				return dm(user_id, message)
			else:
				return False
		self._user_map[user_id] = dm
		return True
		
