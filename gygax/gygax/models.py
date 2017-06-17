from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .app import Session
from .api.slack import Slack as SlackApi
from .util.crypto import rand_key


Base = declarative_base()

assigned_hits = Table('assigned_hits', Base.metadata,
				Column('hit_id', Integer, ForeignKey('hit.id')),
				Column('user_id', Integer, ForeignKey('user.id'))
)

targeted_users = Table('targeted_users', Base.metadata,
				Column('hit_id', Integer, ForeignKey('hit.id')),
				Column('user_id', Integer, ForeignKey('user.id'))
)

# slack_to_user = Table('slack_to_user', Base.metadata,
# 				Column('slack_id', Integer, ForeignKey('slack.id')),
# 				Column('user_id', Integer, ForeignKey('user.id')))


class Query:
	@property
	def query(self):
		return Session().query(self.__class__)

class Slack(Base, Query):
	__tablename__ = 'slack'
	id = Column(Integer, primary_key = True)
	name = Column(String(32))
	slack_id = Column(String(64), unique = True)
	confirmed = Column(Boolean, default = False)
	updated = Column(DateTime(), default=datetime.utcnow)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship("User", backref=backref("slack", uselist=False))

	def __init__(self, slack):
		self.slack_id = slack
		info = SlackApi._get_user_info(slack)
		self.name = info['name'] if info else None

class User(Base, Query):
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	uid = Column(Text, unique = True)
	key = Column(String(128))
	secret = Column(String(128))
	ft_oauth_key = Column(String(64))
	ft_oauth_refresh = Column(String(64))
	assigned = relationship("Hit", secondary=assigned_hits, backref="assigned")
	
	def __init__(self, uid = None, slack = None):
		if not uid and not slack:
			raise Exception('You must provide either uid or slack')
		if uid:
			self.uid = uid
		if slack:
			self.slack = Slack(slack)
		self.key = rand_key()
		self.secret = rand_key()

	def check(self, pwd):
		return hashlib.sha256(pwd).hexdigest() == self.pwd

	@staticmethod
	def from_uid(uid):
		return User.query.filter_by(uid = uid).first()

	@staticmethod
	def from_slack(slack):
		return User.query.filter_by(slack = slack).first()

class Location(Base, Query):
	__tablename__ = 'location'
	id = Column(Integer, primary_key = True)
	desc = Column(Text)

	def __init__(self, desc):
		self.desc = desc

class Weapon(Base, Query):
	__tablename__ = 'weapon'
	id = Column(Integer, primary_key = True)
	desc = Column(Text)

	def __init__(self, desc):
		self.desc = desc

class Hit(Base, Query):
	__tablename__ = 'hit'
	id = Column(Integer, primary_key = True)
	target_id = Column(Integer, ForeignKey('user.id'))
	target = relationship('User', backref='hits')
	weapon_id = Column(Integer, ForeignKey('weapon.id'))
	weapon = relationship('Weapon')
	location_id = Column(Integer, ForeignKey('location.id'))	
	location = relationship('Location')
	conf_code = Column(String(16))
	status = Column(Integer, default = 0)

	def __init__(self, user, target, weapon, location):
		self.assigned = user
		self.target = target
		self.weapon = weapon
		self.location = location
		self.conf_code = utils.gen_confirmation_code()