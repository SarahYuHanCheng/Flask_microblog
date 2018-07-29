from app import create_app, db ,socketio
from app.models import User, Post

app = create_app(debug=True)
# cli.register(app)


@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post, 'Log':Log, 'Comment':Comment, 'Code':Code}
	
if __name__ == '__main__':
	socketio.run(app)