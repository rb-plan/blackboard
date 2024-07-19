from app import app, socketio
from app import Config


if __name__ == '__main__':
    socketio.run(app, debug=True, port=app.config['PORT'], host=app.config['HOST'])

