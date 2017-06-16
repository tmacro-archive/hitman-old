from queue import Queue
from .const import EVENT_TYPES as ETYPES
from collections import defaultdict
from threading import Lock

class Event:
	type = ETYPES.BASE
	def __init__(self, topic, data = {}):
		self._topic = topic
		self._data = data

	def _get(self, key, default = None):
		return self._data.get(key, default)

	def _set(self, key, value):
		self._data[key] = value
		
	@property
	def topic(self):
		return self._topic

	
class Dispatcher:
	'''
		this object manages a list of handlers and associated
		topics, which it uses to dispatch incoming events
	'''
	def __init__(self):
		self._handlers = defaultdict(lambda: defaultdict(list))
		self.__lock = Lock()
	
	def __call__(self, event):
		return self._handle(event)

	def _handle(self, event):
		found = False
		with self.__lock:
			for handler in self._handlers[event.type][event.topic]:
				handler(event)
				found = True
			if not event.topic is None:
				for handler in self._handlers[event.type][None]:
					handler(even)
		return found

	def _register(self, type, topic, handler):
		with self.__lock:
			self._handlers[type][topic].append(handler)

	def register(self, type, topic, handler):
		self._register(type, topic, handler)
