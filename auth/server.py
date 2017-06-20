from hitman.app import app, db
from hitman.models import *

if __name__ == '__main__':
	db.create_all()
	app.run(host='0.0.0.0', port = 8081, debug=True)