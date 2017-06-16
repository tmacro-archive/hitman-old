from gygax.app import app, db
# from gygax.models import *

if __name__ == '__main__':
	db.create_all()
	app.run(host='0.0.0.0', port = 8082, debug=True)