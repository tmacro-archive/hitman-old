from ..models import User
from ..app import db

def commit(model):
	db.session.add(model)
	db.session.commit()

def from_slack(slack):
	return User.from_slack(slack)

def from_uid(uid):
	return User.from_uid(uid)

def create_user(uid = None, slack = None):
	u = User(uid, slack)
	db.session.add(u)
	db.session.commit()
	return u

def get_or_create_user(uid = None, slack = None):
	user = from_uid(uid) if uid else None
	user = from_slack(slack) if not user and slack else None
	if not user:
		return create_user(uid, slack)
	return user

def link_intra(slack, uid, key, refresh):
	user = from_slack(slack)
	user.uid = uid
	user.ft_oauth_key = key
	user.ft_oauth_refresh = refresh
	user.confirmed = True
	commit(user)

def set_intra_key(user, key, refresh):
	user.ft_oauth_key = key
	user.ft_oauth_refresh = refresh
	db.session.add(user)
	db.session.commit()

def set_intra_uid(user, uid):
	user.uid = uid
	db.session.add(user)
	db.session.commit()