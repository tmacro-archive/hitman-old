from .app import db
from .util.crypto import rand_key
assigned_hits = db.Table('assigned_hits',
				db.Column('hit_id', db.Integer, db.ForeignKey('hit.id')),
				db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

targeted_users = db.Table('targeted_users',
				db.Column('hit_id', db.Integer, db.ForeignKey('hit.id')),
				db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	uid = db.Column(db.Text, unique = True)
	slack = db.Column(db.String(21), unique = True)
	slack_confirmed = db.Column(db.Boolean, default = False)
	key = db.Column(db.String(128))
	secret = db.Column(db.String(128))
	ft_oauth_key = db.Column(db.String(64))
	ft_oauth_refresh = db.Column(db.String(64))
	assigned = db.relationship("Hit",
							secondary=assigned_hits,
							backref="assigned")
	def __init__(self, uid):
		self.uid = uid
		self.key = rand_key()
		self.secret = rand_key()

	def check(self, pwd):
		return hashlib.sha256(pwd).hexdigest() == self.pwd

	@staticmethod
	def from_uid(uid):
		return User.query.filter_by(uid = uid).first()

class Location(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	desc = db.Column(db.Text)

	def __init__(self, desc):
		self.desc = desc

class Weapon(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	desc = db.Column(db.Text)

	def __init__(self, desc):
		self.desc = desc

class Hit(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	target = db.relationship('User', backref='hits')
	weapon_id = db.Column(db.Integer, db.ForeignKey('weapon.id'))
	weapon = db.relationship('Weapon')
	location_id = db.Column(db.Integer, db.ForeignKey('location.id'))	
	location = db.relationship('Location')
	conf_code = db.Column(db.String(16))
	status = db.Column(db.Integer, default = 0)

	def __init__(self, user, target, weapon, location):
		self.assigned = user
		self.target = target
		self.weapon = weapon
		self.location = location
		self.conf_code = utils.gen_confirmation_code()