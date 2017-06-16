from ..models import User, Weapon, Location
from ..app import db

def from_slack(slack):
	return User.query.filter_by(slack = slack).first()

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
	
def saveDB(obj):
	db.session.add(obj)
	db.session.commit()