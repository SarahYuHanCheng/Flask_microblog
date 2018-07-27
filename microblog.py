from app import create_app, db ,socketio
from app.models import User, Post

app = create_app()
# cli.register(app)


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post, 'Log':Log, 'Comment':Comment, 'Code':Code}