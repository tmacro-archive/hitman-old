from .app import db
from .util.crypto import rand_key, expiring_token, check_token, token_ttl

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	uid = db.Column(db.Text, unique = True)
	slack = db.Column(db.String(21), unique = True)
	key = db.Column(db.String(128))
	secret = db.Column(db.String(128))
	ft_oauth_key = db.Column(db.String(64))
	ft_oauth_refresh = db.Column(db.String(64))
	confirmed = db.Column(db.Boolean(), default = False)

	def __init__(self, uid = None, slack = None):
		if not uid and not slack:
			raise Exception('You must provide either uid or slack')
		self.uid = uid
		self.slack = slack
		self.key = rand_key()
		self.secret = rand_key()

	@staticmethod
	def from_uid(uid):
		return User.query.filter_by(uid = uid).first()

	@staticmethod
	def from_slack(slack):
		return User.query.filter_by(slack = slack).first()

	def token(self, extra = {}, expires = None, ttl = token_ttl):
		return expiring_token(self.secret, self.key, extra, expires, ttl)
	
	def check(self, token):
		return check_token(self.secret, self.key, token)

	