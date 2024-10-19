from project import app
from waitress import serve
# Cấu hình Web Server
if __name__ == '__main__':
	#serve(app=app, host='127.0.0.1', port=5003)
	app.run(host='0.0.0.0', port=5003, debug=True)
