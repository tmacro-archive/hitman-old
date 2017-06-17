from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict, namedtuple
import json
import re
import urllib.parse as urlparse
from .log import getLogger
from .config import config

_log = getLogger('util.http')


class Request(BaseHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		self._routes = defaultdict(dict)
		super().__init__(*args, **kwargs)

	def _write_resp(self, resp):
		if isinstance(resp, dict):
			resp = json.dumps(resp)
		if not isinstance(resp, bytes):
			resp = resp.encode()
		
		self.wfile.write(resp)

	def _load_req(self):
		length = int(self.headers.get('Content-Length', 0))
		if length:
			blob = self.rfile.read(length)
			return json.loads(blob.decode())
		return None

	def _handle_resp(self, code, resp):
		self.send_response(code)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()
		if resp:
			self._write_resp(resp)
		 	
	def _handle(self, method):
		code, resp = http.handle(method, self.path, self._load_req())
		self._handle_resp(code, resp)

	def do_GET(self):
		self._handle('GET')

	def do_POST(self):
		self._handle('POST')

	def do_PATCH(self):
		self._handle('PATCH')

	def do_PUT(self):
		self._handle('PUT')

	def do_OPTIONS(self):
		self.send_response(200, "ok")
		self.send_header('Access-Control-Allow-Origin', '*')                
		self.send_header('Access-Control-Allow-Methods', 'PATCH, PUT, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "Content-Type")
		self.end_headers()

class Routes(Thread):
	def __init__(self , host = '', port = 80):
		self._routes = defaultdict(list)
		self._server = HTTPServer((host, port), Request)
		super().__init__()
		self.daemon = True
	
	def run(self):
		self._server.serve_forever()

	def join(self, *args):
		self._server.shutdown()
		return super().join(*args)
		
	@staticmethod
	def build_route_pattern(route):
		route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
		return re.compile("^{}$".format(route_regex))

	@staticmethod
	def _parse_query_params(path):
		parsed = urlparse.urlparse(path)
		params = urlparse.parse_qs(parsed.query)
		return {k:v[0] for k,v in params.items()}

	@staticmethod
	def _remove_query_params(path):
		return path.split('?')[0]

	def get_route_match(self, path, method):
		path = self._remove_query_params(path)
		for route in self._routes[method]:
			m = route['pattern'].match(path)
			if m:
				return m.groupdict(), route

		return None

	def route(self, uri, methods=['GET'], params = False):
		if not 'OPTIONS' in methods:
			methods.append('OPTIONS') 
		_log.debug('Registering route %s , methods: %s, params: %s'%(uri, methods, params))
		route_pattern = self.build_route_pattern(uri)
		def decorator(f):
			for method in methods:
				self._routes[method].append(dict(pattern = route_pattern,
												 func = f,
												 params = params))
			return f

		return decorator
	
	def handle(self, method, path, data = None):
		print(method, path, data)
		route_match = self.get_route_match(path, method)
		if route_match:
			kwargs, route = route_match
			view = route['func']
			if route['params']:
				kwargs['params'] = self._parse_query_params(path)
			if method in ['POST', 'PATCH', 'PUT']:
				kwargs["data"] = data

			resp = view(**kwargs)
		else:
			raise ValueError('Route "{}" has not been registered'.format(path))
		
		if isinstance(resp, int):
			return resp, None
		elif not resp:
			return 500, None
		else:
			return 200, resp

http = Routes(config.http.host, config.http.port)
