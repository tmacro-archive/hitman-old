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
	def __init__(self, *args, no_parse = False, **kwargs):
		super().__init__(*args, **kwargs)
		if not no_parse:
			cmd, args = self._parse(self.text)
			self._set('cmd', cmd)
			self._set('args', args)
	
	def _parse(self, text):
		match = re.match(r'^!([a-z]{3,10}) ?([\w ]+)?', self.text)
		cmd = match.group(1) if match else None
		args = match.group(2).split(' ') if match and match.group(2) else []
		return cmd, args

	@property
	def cmd(self):
		return self._get('cmd')
	@property
	def args(self):
		return self._get('args')

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
	
