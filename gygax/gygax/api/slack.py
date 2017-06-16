from ..util.pubsub import Subscriber
from .storage import slack_id_to_slack
from ..util.config import config
from ..util.log import getLogger

_log = getLogger('api.slack')

def subscribe(uri):
	s = Subscriber(uri)
	s.open()
	return s

class Slack:
	def __init__(self, events):
		self._events = events
		self._user_map = {}
		self._subscriber = subscribe(config.firehose.uri)
		self._setup_handlers()

	def _uid_to_slack(uid):
		slack = self._user_map.get(uid)
		if not slack:
			slack = slack_id_to_slack(uid)
		return slack

	def _message_handler(self, message):
		_log.debug('Recieved message %s'%message)

	def _setup_handlers(self):
		self._subscriber.addHandler('msg', self._message_handler, strict = False)

	
