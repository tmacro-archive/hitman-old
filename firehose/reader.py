from hitman.util.config import config
from hitman.util.log import getLogger
from hitman.util.pubsub import Publisher
from slackclient import SlackClient
import time
from Queue import Queue
from Queue import Empty as QueueEmpty
from threading import Thread, Event
import re

_log = getLogger('slack_reader')

class Reader(Thread):
	def __init__(self, token):
		self._client = SlackClient(token)	# create slack client
		self._output = Queue()
		self._exit = Event()
		self._read_int = 1
		super(Reader, self).__init__()
		self.daemon = True					# die on process exit
		self._log = _log.getChild('reader')

	def _handle_event(self, event):
		self._log.debug('got event type: %s'%event['type'])
		self._output.put(event)
	
	@property
	def events(self):
		while not self._exit.isSet():
			try:
				event = self._output.get(True, 5)
				if event:
					yield event
			except QueueEmpty:
				pass
				
	def run(self):
		delay = 1
		self._log.debug('starting reader, initial backoff %i'%delay)
		while not self._exit.isSet():
			self._log.debug('connecting to slack rtm...')
			if self._client.rtm_connect():
				self._log.debug('connected, waiting for events...')
				delay = 2
				while not self._exit.isSet():
					events = self._client.rtm_read()
					for event in events:
						self._handle_event(event)
			else:
				self._log.debug('connection failed')
				if delay <= 16:
					delay += delay
					self._log.debug('increasing backoff to %i'%delay)
				time.sleep(delay)
				

	def join(self):
		self._exit.set()
		self._log.debug('reader exiting...')
		return super(Reader, self).join()					

class Stream:
	def __init__(self, *args):
		self._filters = args
		self._log = _log.getChild('stream')

	def register(self, fltr):
		self._log.debug('registering filter: %s'%filter)
		self._filters.append(fltr)
	
	def _match(self, event):
		topics = [fltr.topic for fltr in self._filters if fltr(event)]
		return list(set(topics))

	def __call__(self, itr):
		for event in itr:
			topics = self._match(event)
			if topics:
				yield event, topics

class Filter(object):
	params = ['type', 'user', 'channel', 'text']
	def __init__(self, **kwargs):
		self._filter = {}
		self._id = kwargs.pop('id') if 'id' in kwargs else 'Filter'
		self._topic = kwargs.pop('topic') if 'topic' in kwargs else 'firehose'
		self._log = _log.getChild(self._id)
		for param in Filter.params:
			 v = kwargs.get(param)
			 if v:
			 	self._filter[param] = v

	@property
	def topic(self):
		return self._topic

	def _check(self, k, v, msg):
		if v in msg.get(k, ''):
			return True
		return False

	def __call__(self, msg):
		for k, v in self._filter.iteritems():
			if self._check(k,v,msg):
				self._log.debug('# %s passed'%self._id)
				return True
		return False

class RegexFilter(Filter):
	def __init__(self, **kwargs):
		Filter.__init__(self, **kwargs)
		compiled = dict()
		for k,v in self._filter.iteritems():
			compiled[k] = re.compile(v)
		self._filter = compiled

	def _check(self, k, v, msg):
		if re.match(v, msg.get(k, '')) is None:
			return False
		return True

class ChannelFilter(Filter):
	@property
	def topic(self):
		return self._topic + self._lastCh.decode()

	def _check(self,k,v, msg):
		if 'channel' in msg:
			self._lastCh = msg.get('channel')
		return super(ChannelFilter, self)._check(k,v,msg)

class TrueFilter(Filter):
	def _check(self, k, v, msg):
		return True

cmd_filter = RegexFilter(text = '^![a-z]+', id = 'CMD_FILTER', topic = 'cmd')
dm_filter = ChannelFilter(type = 'message', id = "DM_FILTER", topic = "ch_")
r = Reader(config.apiSlack.token)
r.start()
s = Stream(cmd_filter, dm_filter)
p = Publisher('ipc://.hitman_events.sock')
p.open()
for event, topics in s(r.events):
	if topics:
		p.publish('firehose', event)
	for topic in topics:
		p.publish(topic, event)