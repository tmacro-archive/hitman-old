'''
	This module defines subclasses of Action which define 
	how the bot reacts to specfic events. These reactions 
	can range from a simple database modification, to a external 
	http request, to more events be push into the queue. 
	It is from these interactions that arise what one might call intelligence.
'''
from ..util.log import getLogger
from .const import CMD_TYPES as CTPYES
from .const import EVENT_TYPES as ETYPES
from ..api.storage import from_slack, create_user, validate_slack, set_weapon, set_location, info_locked
from ..util.http import http
from .events import SlackValidationEvent, MessageEvent, CommandEvent, SendMessageEvent
from ..api import auth as AuthApi
from ..app import slack as SlackApi
from ..util.config import config
_log = getLogger('action')

class Action:
	def __init__(self, proxy):
		self._proxy = proxy
		self._log = _log.getChild(self.__class__.__name__)
		self._install(proxy)

	def __call__(self, msg):
		return self._process(msg)

	def _install(self, proxy):
		pass

	def _process(self, msg):
		self._log.debug('Got message, Taking no action')
		return True

	def _register(self, *args, **kwargs):
		return self._proxy.register(*args, **kwargs)

	def _put(self, event):
		return self._proxy.put(event)

class CommandAction(Action):
	'''
		This action processes a raw command and 
		pushes the generated event onto the queue
	'''
	def _install(self, proxy):
		proxy.register(ETYPES.CMD, 'cmd_raw', self)

	def _process(self, event):
		self._log.debug('Processing raw command')
		print(event.data())
		if event.cmd_type == 'bang':
			if not SlackApi._is_dm(event.channel):
				self._log.debug('bang command on public channel')
				ev = SendMessageEvent('msg_send', dict(channel=event.channel, text=config.resp.public_bang))
				return self._put(ev)
		if event.cmd and event.cmd.upper() in CTPYES._fields:
			ev = CommandEvent('cmd_%s'%event.cmd, event.data(), no_parse = True)
			self._log.debug('CommandEvent validated setting topic to %s and pushing to queue'%ev.topic)
			self._put(ev)
			return True

class RegisterAction(Action):
	'''
		This action begins the user registration process.
		It creates a user in the database if one does not exist,
		and generates an event to obtain a registration link to the auth service
	'''
	def _install(self, proxy):
		proxy.register(ETYPES.CMD, 'cmd_register', self)

	def _process(self, event):
		self._log.debug('Recieved registration command for user %s'%event.user)
		user = from_slack(event.user)
		if not user:
			user = create_user(slack = event.user)
			self._log.info('Created account for %s'%user.slack.name)
		if not user.slack.confirmed:
			self._log.debug('Pushing SlackValidationEvent for %s'%event.user)
			ev = SlackValidationEvent('user_validate', dict(user=event.user))
		else:
			self._log.debug('user %s already in database'%event.user)
			ev = SendMessageEvent('msg_send', dict(user=event.user, text=config.resp.already_registered))				
		self._put(ev)		

class ValidateSlackAction(Action):
	'''
		This actions checks if a slack user needs authorizing,
		if so it querys the auth service for a validation url,
		then push a message to the slack user containg the url
	'''
	def _install(self, proxy):
		proxy.register(ETYPES.USER, 'user_validate', self)

	def _process(self, event):
		self._log.debug('Recieved slack validation event for %s'%event.user)
		if event.validated:
			if validate_slack(event.user, event.uid):
				user = from_slack(event.user)
				self._log.info('Successfully linked 42 uid %s with slack %s'%(user.uid, user.slack.name))
				ev = SendMessageEvent('msg_send', dict(user=event.user, 
									template=config.resp.registration_success,
									args=dict(uid=user.uid)))
				self._put(ev)
			else:
				self._log.error('Failed to link 42 uid %s with slack %s'%(event.uid, event.user))
		elif not event.validated and event.failed:
			self._log.error('Failed to validate slack user %s, they probably denied our oauth request'%event.user)
		else:
			self._log.debug('Generating validation url for %s'%event.user)
			uid, url = AuthApi.validate_user(event.user)
			if not url and not uid:
				self._log.error('Failed to retrieve validation url for slack user %s'%event.user)
				ev = SendMessageEvent('msg_send', dict(user=event.user, text=config.resp.register_error))
			elif url:
				self._log.debug('Retrieved vaidation url for %s'%event.user)
				ev = SendMessageEvent('msg_send', dict(user=event.user, template=config.resp.validation, args=dict(url=url)))
			elif uid:
				self._log.debug('slack user %s is already authenticated'%event.user)
				validate_slack(event.user, uid)
				ev = SendMessageEvent('msg_send', dict(user=event.user, text=config.resp.already_registered))				
			self._put(ev)



class SlackAuthorizedAction(Action):
	'''
		This action monitors an http endpoint,
		and pushes a user validation event upon acivity
	'''
	@http.route('/slack_authorized', methods = ['POST'], params = True)
	def _callback(self, data = None, params = None):
		self._log.debug('Recieved notification of slack validation')
		if params:
			data = dict(
				user = params.get('user'),
				valid = params.get('valid'),
				uid = params.get('uid'),
				failed = not params.get('valid')
			)
			if data['user'] and (not data['valid'] or data['uid']):
				ev = SlackValidationEvent('user_validate', data)
				self._put(ev)
				self._log.debug('Recieved slack validation for user %s 42 uid %s'%(ev.user, ev.uid))
		self._log.warning('Malformed request from authentication server')

class SendMessageAction(Action):
	def _install(self, proxy):
		proxy.register(ETYPES.MSG, 'msg_send', self)

	def _process(self, event):
		self._log.debug('Recieved outbound message event to %s'%event.user)
		if not event.text:
			self._log.error('Outbound message has no text!')
			return
		if event.channel:
			ok = SlackApi.msg(event.channel, event.text)
		else:
			ok = SlackApi.dm(event.user, event.text)
		if ok:
			self._log.debug('Successfully sent message to %s'%event.user)
		else:
			self._log.debug('Failed to send message to %s'%event.user)

class CollectInfoAction(Action):
	def _install(self, proxy):
		proxy.register(ETYPES.USER, 'user_info', self)
		
	def _process(self, event):
		self._log.debug('Recieved info collection event for user %s'%event.user)
		ev = SendMessageEvent('msg_send', dict(user=event.user, text = config.resp.collect_info))
		self._put(ev)

class SetInfoAction(Action):
	def _install(self, proxy):
		proxy.register(ETYPES.CMD, 'cmd_set', self)

	def _process(self, event):
		self._log.debug('Recieved set info event for user %s'%event.user)
		if not event.args:
			ev = SendMessageEvent('msg_send', dict(user=event.user, text = config.resp.info_set_usage))
			self._put(ev)
			return
		target = event.args[0]
		if not target in ['weapon', 'location']:
			ev = SendMessageEvent('msg_send', dict(user=event.user, text = config.resp.info_set_usage))
		else:
			if info_locked(event.user):
				ev = SendMessageEvent('msg_send', dict(user=event.user, text = 'You can;t update your %s in the middle of a game!'%target))
			value = ' '.join(event.args[1:])
			self._log.debug("Updating %s's %s to %s"%(event.user, target, value))
			ok = True
			if target == 'weapon':
				if not set_weapon(event.user, value):
					ok = False
			if target == 'location':
				if not set_location(event.user, value):
					ok = False
			if ok:
				ev = SendMessageEvent('msg_send', dict(user=event.user, 
												template = config.resp.info_set_confirm, 
												args = dict(key=target, value=value)))
			else:
				ev = SendMessageEvent('msg_send', dict(user=event.user,
												text = 'There was a probem updating you %s, please try again'%target))
		self._put(ev)	