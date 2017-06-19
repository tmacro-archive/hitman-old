from .crypto import check_token, expiring_token, token_ttl
from .config import config



class UserSession:
	def __init__(self, **kwargs):
		self._data = kwargs
		
	def _get(self, k, d = None):
		return self._data.get(k,d)

	def _set(self, k, v):
		self._data[k] = v
	
	@property
	def data(self):
		return self._data.copy()

	@property
	def valid(self):
		token = self._get('token')
		if not token:
			return False
		elif not check_token(config.crypto.secret, config.crypto.key, token):
			return False
		return True
	
	def validate(self):
		self._set('token', expiring_token(config.crypto.secret, 
										  config.crypto.key))

	@property
	def slack(self):
		return self._get('slack')

	@slack.setter
	def slack(self, v):
		self._set('slack', v)

	@property
	def slack_token(self):
		return self._get('slack_token')

	@slack_token.setter
	def slack_token(self, v):
		self._set('slack_token', v)

	@property
	def uid(self):
		return self._get('uid')

	@uid.setter
	def uid(self, v):
		self._set('uid', v)

	@property
	def ft_token(self):
		return self._get('ft_token')

	@ft_token.setter
	def ft_token(self, v):
		self._set('ft_token', v)

	@property
	def	ft_refresh(self):
		return self._get('ft_refresh')
	
	@ft_refresh.setter
	def ft_refresh(self, v):
		self._set('ft_refresh', v)