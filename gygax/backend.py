from app import db
from models import Hit, User, Weapon, Location
import hashlib

def login(uid, pwd):
	user = User.from_uid(uid)
	if user.pwd == hashlib.sha256(pwd).hexdigest():
		return True
	return False

def getHits(uid):
	hits = {}
	for hit in Hit.select():
		if hit.uid == uid:
			hits[hits.target] = {
						hit.status,
						hit.weapon.desc,
						hit.location.desc
						}

	return hits

def completeHit(uid, code):
	hit = Hit.get(Hit.code == code)
	if hit.uid == uid:
		hit.status = 'TERMINATED'
		hit.save()
		return hit.target
	return False

def reassignHit(current, new):
	hit = Hit.get(Hit.uid == current)
	hit.uid = new
	hit.save()
	return {
			hit.target: {
						hit.status,
						hit.weapon.desc,
						hit.location.desc,
						}
			}

def createItems(weapon, location):
	w = Weapon.create()
	w.desc = weapon
	l = Location.create()
	l.desc = location
	w.save()
	l.save()
