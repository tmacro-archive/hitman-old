#!/usr/bin/python2

import sys
from collections import defaultdict
from getpass import getpass
from StringIO import StringIO
from hashlib import sha512
from httplib import HTTPConnection, HTTPSConnection
from urllib import urlencode
from urlparse import urlparse
import json
import webbrowser

class SimpleNamespace:
	pass

root_endpoint = 'http:/hitman.tmacs.space'
class endpoints:
	register = root_endpoint + '/register'
	login	= root_endpoint + '/login'
	hits = root_endpoint + '/targets'
	report = root_endpoint + '/report'

class config:
	endpoints = endpoints

# Utility functions
def getInput(prompt):
	return raw_input(prompt)

def getPass(prompt):
	stream = StringIO()
	print prompt,
	getpass('', stream)
	print '' 
	return sha512(stream.read()).hexdigest()

def getLogin(default = None):
	if default:
		u = getInput('Enter your intra login(%s: '%default)
	else:
		u = getInput('Enter your intra login: ')
	pwd = getPass('Enter your hitman password: ')
	return u, pwd

class constructordict(dict):
	def __init__(self, constructor, *args, **kwargs):
		self._constr = constructor
		self._args = args
		self._kwargs = kwargs

	def __getitem__(self, key):
		if not key in self.keys():
			return self._constr(*self._args, **self.kwargs)
		return super(constructordict).__getitem__(key)

class Arg:
	'''
		A class to handle streams of arguements
	'''
	def __init__(self, args, pos = 0):
		self._args = args
		self._pos = pos

	def __call__(self):
		return self.asStr

	def __str__(self):
		return self.asStr
	
	def __repr__(self):
		return '<Arg pos: %i, %s>'%(self._pos, self())
	
	def _posValid(self, dif):
		if self._pos + dif < 0 or self._pos + dif >= len(self._args):
			return False
		return True
	
	def _iterArg(self, dif):
		if not dif is None:
			start = 1 if dif > 0 else dif
			stop = dif if dif > 0 else 0
		else:
			start = 1
			stop = len(self._args) - self._pos
		for x in range(start, stop):
			if self._posValid(x):
				yield Arg(self._args, self._pos + x)

	@property
	def next(self):
		if self._posValid(1):
			return Arg(self._args, self._pos + 1)
		return None

	@property
	def prev(self):
		if self._posValid(-1):
			return Arg(self._args, self._pos - 1)
		return None

	@property
	def asStr(self):
		return str(self._args[self._pos])

	def nextn(self, num = None):
			return [x for x in self._iterArg(num)]

	def prevn(self, num):
			return [x for x in self._iterArg(num * -1)]

class Nine:
	'''
		A barebones framework for handling commandline flags
	'''
	def __init__(self):
		self._handlers = defaultdict(list)
		self._config = defaultdict(list)
		self.__config = SimpleNamespace()

	def cmd(self, cmd, long = None, args = False):
		def decorator(f):
			self._handlers[cmd].append(dict(
									cmd = cmd, 
									long = long,
									func = f,
									args = args))
			self._handlers[long].append(dict(see=cmd))
			return f
		return decorator
	
	def config(self, stage = 20):
		def decorator(f):
			self._config[stage].append(f)
			return f
		return decorator

	def _getHandlers(self, arg):
		for handler in self._handlers[arg.asStr]:
			if 'cmd' in handler:
				yield handler['func'], handler['args']
			elif 'see' in handler:
				self._getHandlers(handler['see'])

	def _hasHandlers(self, arg):
		return len(list(self._getHandlers(arg))) > 0
		
	def _parse_config(self):
		for level in sorted(self._config.keys()):
			for c in self._config[level]:
				c(self.__config)

	def _parse_args(self):
		for arg in Arg(sys.argv).nextn():
			for handler, args in self._getHandlers(arg):
				if args:
					handler(self.__config, arg)
				else:
					handler(self.__config)

	def parse(self):
		self._parse_config()
		return self._parse_args()

n = Nine()

class Response:
	def __init__(self, resp):
		self.status = resp.status
		self._raw = resp.read()
		self.headers = dict()
		for k, v in resp.getheaders():
			self.headers[k] = v
	
	@property
	def body(self):
		return self._raw

	@property
	def json(self):
		return json.loads(self.body)

class Request:
	def __init__(self, method, addr, params = None, data = None):
		self._method = method
		self._parse_addr(addr)
		self._params = params
		self._data = data

	def _parse_addr(self, addr):
		p = urlparse(addr)
		self._host = p.netloc
		self._proto = p.scheme
		self._path = p.path
	
	def _build(self):
		if self._proto == 'https':
			return HTTPSConnection(self._host)
		else:
			return HTTPConnection(self._host)

	def _make(self):
		conn = self._build()
		headers = {'Content-Type':'application/json'} if self._data else {}
		path = self._path + '?' + urlencode(self._params) if self._params else self._path
		body = json.dumps(self._data) if self._data else None
		if body:
			conn.request(self._method, path, body, headers)
		else:
			conn.request(self._method, path, None, headers)
		return self._resp(conn)

	def _resp(self, conn):
		return Response(conn.getresponse())
		
	def do(self):
		return self._make()
		

		
class requests:
	'''
		A simple wrapper for HTTPConnection objects
	'''
	@staticmethod
	def get(*args, **kwargs):
		req = Request('GET', *args, **kwargs)
		return req.do()
	
	@staticmethod
	def post(*args, **kwargs):
		return Request('POST', *args, **kwargs).do()



@n.cmd('register')
def register(cfg):
	user, pwd = getLogin()
	weapon = getInput('Choose a weapon: ')
	loc = getInput('Choose a location: ')
	resp = requests.post(endpoints.register, data = dict(uid=user, pwd = pwd, weapon = weapon, location = loc))
	print resp.body
	webbrowser.open('https://google.com', 2)

@n.cmd('login')
def login(cfg):
	user, pwd = getLogin()
	resp = requests.post(endpoints.info, data = dict(uid=user, pwd = pwd))
	print resp.body



if __name__ == '__main__':



	n.parse()