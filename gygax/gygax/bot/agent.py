from threading import Thread, Event
from queue import Queue, Empty
from .dispatch import Dispatcher, Proxy
from ..util.log import getLogger
from ..util.config import config

_log = getLogger('bot.agent')

class Agent(Thread):
	def __init__(self):
		self._events = Queue()
		self._dispatch = Dispatcher()
		self._proxy = Proxy(self._dispatch, self.put)
		self._exit = Event()
		super().__init__()

	def _get(self):
		try:
			return self._events.get(True, 1)
		except Empty:
			pass
		return None
	
	def put(self, event):
		self._events.put(event)

	@property
	def proxy(self):
		return self._proxy
		
	def _handle(self, event):
		_log.debug('Handling event type: %s, topic: %s'%(event.type, event.topic))
		handled = self._dispatch(event)
		if not handled:
			_log.debug('No handlers were found for event')

	def run(self):
		_log.debug('Starting agent, waiting for events...')
		while not self._exit.isSet():
			event = self._get()
			if event:
				_log.debug('A wild Event appeared!')
				self._handle(event)
		_log.debug('Exiting.')

	def join(self, timeout = 0):
		self._exit.set()
		return super().join(timeout)