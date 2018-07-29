from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User, Log, Code
from flask_login import current_user
from app.games import current_game,current_log,current_code

class CommitCodeForm(FlaskForm):
	body = TextAreaField('Code', validators=[DataRequired(),Length(min=0, max=10240)])
	commit_msg = TextAreaField('Commit msg', validators=[DataRequired(),Length(min=0, max=140)])
	commit = SubmitField('Commit')
	log_id = HiddenField('Log id', default=current_log)

	# def __init__(self, original_log, *args, **kwargs):
	# 	super(CommitCodeForm, self).__init__(*args, **kwargs)
	# 	self.original_log = original_log

class StartGameForm(FlaskForm):
	game_id = HiddenField('Game id', default=current_game)
	userId =current_user
	user_id = HiddenField('User id', default=userId)
	start = SubmitField('Start Game')

	# def __init__(self, arg):
	# 	super(StartGameForm, self).__init__()
	# 	self.arg = arg

class CreateGameForm(FlaskForm):
	user_id = HiddenField('User id', default=current_user)
	gamename = TextAreaField('gamename', validators=[DataRequired()])
	descript = TextAreaField('descript', validators=[DataRequired()])
	game_lib = TextAreaField('game_lib', validators=[DataRequired()])
	example_code = TextAreaField('example code', validators=[DataRequired()])
	create = SubmitField('Create Game')

class CommentCodeForm(FlaskForm):
	body = TextAreaField('Comment', validators=[DataRequired(),Length(min=0, max=1024)])
	user_id = HiddenField('User id', default=current_user)
	code_id = HiddenField('Code id', default=current_code)
	comment = SubmitField('Comment')
	# def __init__(self, arg):
	# 	super(CreateGameForm, self).__init__()
	# 	self.arg = arg



	# def validate_username(self,username):
	# 	if username.data != self.original_username:
	# 		user = User.query.filter_by(username=self.username.data).first()
	# 		if user is not None:
	# 			raise ValidationError('Please use a different username.')
class LoginForm(FlaskForm):
    """Accepts a nickname and a room."""
    name = StringField('Name', validators=[DataRequired()])
    room = StringField('Room', validators=[DataRequired()])
    submit = SubmitField('Enter Chatroom')
