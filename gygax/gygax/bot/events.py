from .dispatch import Event
from .const import EVENT_TYPES as ETYPES
import re

class MessageEvent(Event):
	type  = ETYPES.MSG
	@property
	def text(self):
		return self._get('text')

	@property
	def user(self):
		return self._get('user')

	@property
	def channel(self):
		return self._get('channel')

class CommandEvent(MessageEvent):
	type = ETYPES.CMD
	bang_cmd = r'^!(?P<cmd>[a-z]{3,10})(?:[ \t]+(?P<args>[\w ]+))?'
	at_cmd = r'^<@(?P<user>\w+)>\s(?P<cmd>[a-z]{3,10})(?:[ \t]+(?P<args>[\w ]+))?'
	def __init__(self, *args, no_parse = False, **kwargs):
		super().__init__(*args, **kwargs)
		if not no_parse:
			type, cmd, args = self._parse(self.text)
			self._set('cmd_type', type)
			self._set('cmd', cmd)
			self._set('args', args)
	
	def _parse_args(self, args):
		if not args is None:
			return args.split(' ')

	def _parse(self, text):
		match = re.match(self.bang_cmd, self.text)
		if match:
			return 'bang', match['cmd'], self._parse_args(match['args'])
		match = re.match(self.at_cmd, text)
		if match:
			return 'at', match['cmd'], self._parse_args(match['args'])
		return cmd, args

	@property
	def cmd(self):
		return self._get('cmd')
	@property
	def args(self):
		return self._get('args')
	
	@property
	def cmd_type(self):
		return self._get('cmd_type')

class SlackValidationEvent(Event):
	type = ETYPES.USER
	@property
	def user(self):
		return self._get('user')

	@property
	def validated(self):
		return self._get('valid', False)

	@property
	def failed(self):
		return self._get('failed', False)

	@property
	def uid(self):
		return self._get('uid')

class SendMessageEvent(MessageEvent):
	type = ETYPES.MSG
	@property
	def text(self):
		if self.template and self.args:
			return self.template.format(**self.args)
		return self._get('text', '')
	
	@property
	def template(self):
		return self._get('template')
	
	@property
	def args(self):
		return self._get('args')

	
