# from gygax.app import app
# from gygax.models import *
from gygax.app import agent, slack, db
from gygax.models import User, Weapon, Location, Slack, Base
from gygax.util.http import http
Base.metadata.create_all(db)
agent.start()
slack.start()
http.start()
if __name__ == '__main__':
	# db.create_all()
	# app.run(host='0.0.0.0', port = 8082, debug=True)
	input()