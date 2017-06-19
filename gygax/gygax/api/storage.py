from ..models import User, Weapon, Location, Slack
from ..app import Session
from ..util.log import getLogger

_log = getLogger(__name__)

def session(f):
	'''
		Creates a new database session per call
		wrapped functions should return a 2-tuple 
		of  1) a list of models to be added to the session
		and 2) value to return. If None, models from 1 will be returned
		optionally wrapped functions can return a 3-tuple
		with 3) value to return should commit the session fail
	'''
	def decarator(*args, **kwargs):
		session = Session()
		ret = f(session, *args, **kwargs)
		try:
			if ret[0]:
				for m in ret[0]: 
					session.merge(m)
				session.commit()
		except Exception as e:
			_log.warning('Failed to commit session to db with %s'%e)
			_log.exception(e)
			if len(ret) == 3:
				session.close()
				return ret[2]
		if ret[1] is None:
			if not ret[0] is None and len(ret[0]) == 1:
				return ret[0][0]
			return ret[0]
		return ret[1]
	return decarator

def query(f):
	'''
		Creates a new database query from the given model
	'''
	@session
	def inner(s, *args, **kwargs):
		q = s.query
		r = f(q, *args, **kwargs)
		return None, r
	return inner

@query
def from_slack(query, slack):
	u = query(Slack).filter_by(slack_id = slack).first()
	return u.user if u else None

def from_uid(uid):
	return User.query.filter_by(uid = uid).first()

def from_slack_id(slack_id):
	return User.query.filter_by(slack_id = slack_id).first()

def slack_id_to_slack(slack_id):
	user = from_slack_id(slack_id)
	return user.slack if user else None

def slack_to_slack_id(slack):
	user = from_slack(slack)
	return user.slack_id if user else None

@session
def create_user(session, **kwargs):
	u = User(**kwargs)
	return [u], None
	
@session
def validate_slack(session, slack, uid = None):
	user = from_slack(slack)
	if user:
		user.slack.confirmed = True
		user.uid = uid
		return [user], True, False
	return None, False
	
def saveDB(obj):
	db.session.add(obj)
	db.session.commit()