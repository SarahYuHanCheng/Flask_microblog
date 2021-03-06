from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User, Log, Code, Game
from flask_login import current_user
from app.games import current_game,current_log,current_code


class ChooseGameForm(FlaskForm):
	game_category = SelectField('Game Category',# ) coerce=int
		choices=[('1', 'one player'), ('2', 'two players'), ('3','3 players')])
	game =  SelectField('Game',# ) coerce=int
		choices=[('1', 'maze'), ('2', 'pinpong'), ('3', 'shoot')])
	user_id = HiddenField('User id', default=current_user)
	player_list = TextAreaField('player_list')
	start = SubmitField('choose Game')

	# def __init__(self, arg):
	# 	super(StartGameForm, self).__init__()
	# 	self.arg = arg
		# user = Game.query.filter_by(username=self.username.data).first()
		# form = ChooseGameForm() # 這樣寫對嗎？
		# form.game_category.choices = [(g.id, g.gamename) for g in Game.query.order_by('category_id')]	 


	# def game_list(self,request, game_category):
	# 	user = Game.query.filter_by(username=self.username.data).first()
	# 	form = ChooseGameForm() # 這樣寫對嗎？
	# 	form.game_category.choices = [(c.id, c.name) for c in Category.query.order_by('category_id')]	
	# 	form.game.choices = [(g.id, g.gamename) for g in Game.query.order_by('game_id')] # join Game_Category
	# 	form.game.choices = [(g.id, g.gamename) for g in Game.query.order_by('category_id')]	
		
	# 	submit = SubmitField('Enter Gameroom')


class CreateGameForm(FlaskForm):
	user_id = HiddenField('User id', default=current_user)
	gamename = TextAreaField('gamename', validators=[DataRequired()])
	descript = TextAreaField('descript', validators=[DataRequired()])
	player_num = IntegerField('player_num')
	category_id = IntegerField('category_id')

	game_lib_id = TextAreaField('game_lib_id')#, validators=[DataRequired()]
	example_code = TextAreaField('example code')# , validators=[DataRequired()]
	language = SelectField(
		'Programming Language',
		choices=[('cpp', 'C++'), ('py', 'Python'), ('js', 'Javascript')]
	)
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
class AddRoomForm(FlaskForm):
	game_category = SelectField('Game Category',# ) coerce=int
		choices=[('1', 'one player'), ('2', 'two players'), ('3','3 players')])
	game =  SelectField('Game',# ) coerce=int
		choices=[('1', 'maze'), ('2', 'pinpong'), ('3', 'shoot')])
	user_id = HiddenField('User id', default=current_user)
	privacy =  SelectField('privacy',
		choices=[('1', 'public'), ('2', 'friends'), ('3', 'invited')])
	players_status = IntegerField('players_status')
	submit = SubmitField('Enter Gameroom')
	

  #   def validate_gamename(self, room_name):
		# room = Room.query.filter_by(room_name=room_name.data).first()
		# if room is not None:
		# 	raise ValidationError('Please use a different roomname.')
	



class LoginForm(FlaskForm):
	"""Accepts a nickname and a room."""
	name = StringField('UserName', validators=[DataRequired()])
	room = StringField('GameRoomId', validators=[DataRequired()])
	submit = SubmitField('Enter Chatroom')

class JoinForm(FlaskForm):
	submit = SubmitField('Join game')
class LeaveForm(FlaskForm):
	submit = SubmitField('Leave Chatroom')
