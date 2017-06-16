from flask import request
from models import *
import hashlib
import json
from app import app, db
from backend import createItems, getHits, completeHit, reassignHit
from utils import form_data
#create flask app

@app.route("/register", methods = ['POST'])
def register():
	print(request.headers)
	uid = request.json.get('uid')
	pwd = request.json.get('pwd')
	weapon = request.json.get('weapon')
	loc = request.json.get('location')
	if uid and pwd and weapon and loc:
		user = User.query.filter(uid)
		print(user)
		if user:
			return '451'
		else:
			u = User(uid, pwd)
			db.session.add(u)
			w = Weapon(weapon)
			l = Location(loc)
			db.session.add(l)
			db.session.add(w)
			sb.session.commit()
			return 'success'
	return '503'

@app.route("/targets", methods = ["POST"])
def targets():
	data = request.get_json()
	if data.get('uid') and data.get('pass'):
		if login(data['uid'], data['pass']):
			hits = getHits(request['uid'])
			return json.dumps(hits)
	return 400

@app.route("/report", methods = ['POST'])
def report():
	if request.form.get('uid', False) and requests.form.get('pass', False):
		target = completeHit(request.form['uid'], request.form['code'])
		if target:
			hit = reassignHit(target, request.form['uid'])
			return json.dumps(hit)
	return 400

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug = True)
