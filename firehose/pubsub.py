import zmq
import threading
import json
import time
from collections import defaultdict
from .log import getLogger
moduleLogger = getLogger(__name__)

class HandlerNotFound(Exception):
	pass

class InvalidArguements(Exception):
	pass

class RPCError(Exception):
	pass

class Message(object):
	def __init__(self):
		self._payload = {}

	@property
	def payload(self):
		return self._payload

	def setOption(self, key, value):
		self._payload[key] = value

	def getOption(self, key, default = None):
		return self._payload.get(key, default)

class Event(Message):
	def __init__(self, topic, event = {}):
		super(Event, self).__init__()
		self.setOption('topic', topic)
		self.setOption('event', event)

	@property
	def topic(self):
		return self.getOption('topic')

	@property
	def event(self):
		return self.getOption('event')

	@property
	def type(self):
		return self.getOption('event', {})['type']

class Transport(threading.Thread):
	def __init__(self, path):
		self._log = moduleLogger.getChild('transport %s'%path)
		self._path = path
		self._exit = threading.Event()
		self._watched = False
		super(Transport, self).__init__()

	def open(self):
		self._log.debug('opening socket')
		self._context = zmq.Context()
		self._socket = self._context.socket(self.type)
		if self.type == zmq.PUB:
			self._log.debug('transport type is publisher, binding to socket')
			self._socket.bind(self._path)
		elif self.type == zmq.SUB:
			self._log.debug('transport type is subscriber, connecting to socket')
			self._socket.connect(self._path)

	def _pack_event(self, topic, event):
		msg = json.dumps(event)
		return '%s %s'%(topic, msg)

	def _unpack_event(self, msg):
		topic = msg.split(' ')[0]
		event = ' '.join(msg.split(' ')[1:])
		return topic, json.loads(event)

	def _recv(self, noError = False,):
		if self._watched and not noError:
			raise RPCError('you cannot recieve on a watched connection')
		try:
			self._log.debug('waiting for incoming data')
			data = self._socket.recv_string()
			topic, msg = self._unpack_event(data)
		except zmq.ZMQError:
			return None
		except ValueError:
			raise RPCError('Malformed message body')
		self._log.debug('recieved message %s'%data)
		self._log.debug('returning Event')
		return Event(topic, msg)

	def _send(self, msg):
		data = self._pack_event(msg.topic, msg.event)
		self._log.debug('sending data %s'%data)
		self._socket.send_string(data)

	def _close(self):
		if self._watched:
			self._exit.set()
		self._socket.close()

	def _watch(self, handler):
		self._log.debug('setting up watcher')
		self._handler = handler
		self._watched = True
		self.start()

	def run(self):
		self._log.debug('watching for data')
		while not self._exit.isSet():
			message = self._recv(noError = True)
			if message:
				self._log.debug('message recieved')
				self._handler(message)
			else:
				time.sleep(1)

class Subscriber(Transport):
	def __init__(self, path):
		super().__init__(path)
		self._log = moduleLogger.getChild('publisher: %s'%path)
		self._handlers = defaultdict(list)
		self.type = zmq.SUB

	def open(self):
		super().open()
		self._watch(self._process)

	def addHandler(self, topic, func, mapping = {}, strict = True): #mapping defines optional a required arguements eg {'foo': True, 'bar': False}
		self._handlers[topic].append(dict(func = func, args = mapping, strict = strict))
		self._subscribe(topic)
	
	def _subscribe(self, topic):
		self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)

	def _handle(self, topic, message):
		handlers = self._handlers.get(topic, None)
		if not handlers:
			raise HandlerNotFound('No handler found for %s'%topic)
		else:
			for handler in handlers:
				if handler['strict']:
					required = [x for x, y in handler['args'].iteritems() if y] # These args are required
					optional = [x for x, y in handler['args'].iteritems() if not y] # and these are optional
					for arg in message.keys():
						if arg in required:
							required.remove(arg)
						elif not arg in optional:
							raise InvalidArguements('extra arguement %s provided'%arg)
					if required:
						raise InvalidArguements('Not all required arguements provided %s'%required)
				handler['func'](message)

	def _process(self, message):
		try:
			result = self._handle(message.topic, message.event)
		except HandlerNotFound as e:
			return dict(success = False, error = 'HandlerNotFound')

		except InvalidArguements as e:
			return dict(success = False, error = str(e))

		return dict(success = True, results = result)

	def _messageHandler(self, message):
		response = Response(**self._call(message))
		self._send(response)

class Publisher(Transport):
	def __init__(self, path):
		self._log = moduleLogger.getChild('publisher: %s'%path)
		self.type = zmq.PUB
		super(Publisher, self).__init__(path)
	
	def _publish(self, msg):
		self._send(msg)

	def publish(self, topic, event):
		msg = Event(topic, event)
		return self._publish(msg)