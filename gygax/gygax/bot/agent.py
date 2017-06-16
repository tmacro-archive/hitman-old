from threading import Thread, Event
from queue import Queue, Empty
from .dispatch import Dispatcher
from ..util.log import getLogger
from ..util.config import config

_log = getLogger('bot.agent')

class Agent(Thread):
	def __init__(self):
		self._events = Queue()
		self._dispatch = Dispatcher()
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
	def exit(self):
		return not self._exit.isSet()

	@exit.setter
	def exit(self, value):
		if value:
			self._exit.set()

	def _handle(self, event):
		_log.debug('Handling event type: %s, topic: %s'%(event.type, event.topic))
		handled = self._dispatch(event)
		if not handled:
			_log.debug('No handlers were found for event')

	def run(self):
		while not self.exit:
			item = self._get()
			if item:
				self._handle(event)