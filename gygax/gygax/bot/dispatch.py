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
	
	@topic.setter
	def topic(self, topic):
		self._topic = topic

	def data(self, data = None, overwrite = False):
		if not data and  not overwrite:
			return self._data.copy()
		data = data if not data is None else {}
		if overwrite:
			self._data = data
		else:
			self._data.update(data)
			

class Proxy:
	def __init__(self, disp, queue):
		self.__disp = disp
		self.__queue = queue
	
	def register(self, *args, **kwargs):
		return self.__disp.register(*args, **kwargs)

	def put(self, event):
		self.__queue(event)

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
			if not event.topic == None:
				for handler in self._handlers[event.type][None]:
					handler(event)
		return found

	def _register(self, type, topic, handler, oneshot = False):
		with self.__lock:
			self._handlers[type][topic].append(handler)

	def register(self, type, topic, handler, oneshot = False):
		self._register(type, topic, handler, oneshot)
