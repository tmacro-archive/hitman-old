import signal
import sys
from gygax.app import agent, slack, db
from gygax.util.http import http

def start_agent():
	agent.start()
	slack.start()
	http.start()

def create_tables():
	from gygax.models import User, Weapon, Location, Slack, Base
	Base.metadata.create_all(db)

def sig_handler(sig, frame):
	slack.stop()
	agent.join(10)
	sys.exit(0)

if __name__ == '__main__':
	# db.create_all()
	# app.run(host='0.0.0.0', port = 8082, debug=True)
	signal.signal(signal.SIGINT, sig_handler)
	signal.signal(signal.SIGTERM, sig_handler)
	create_tables()
	start_agent()
	signal.pause()
