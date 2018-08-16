from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, StartGameForm, CommitCodeForm,CommentCodeForm,ChatForm, OpenRoomForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Comment, Game, Log, Code, Comment
from werkzeug.urls import url_parse
from datetime import datetime
from app.games import bp, current_game, current_log, current_code, current_comment
from websocket import create_connection
import json, sys

current_game = '3333'
# print(current_log)
class ComplexDecoder(json.JSONDecoder):
	def default(obj):
		return json.JSONDecoder.default(obj)
class ComplexEncoder(json.JSONEncoder):
	def default(self, obj):
		import datetime
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)

def obj_to_json(obj_list):
	out = [q.__dict__ for q in obj_list]
	for objs, instance in zip(out, obj_list):
		for obj in objs.values():
			if callable(obj):
				for name in obj.mapper.relationships.keys():
					tmp = getattr(instance, name).__dict__
					if "_sa_instance_state" in tmp.keys():
						tmp.pop("_sa_instance_state")
						tmp.pop("id")
						objs.update(tmp)
					objs.pop(name)
		if "_sa_instance_state" in objs.keys():
			objs.pop("_sa_instance_state")
	return out
@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
	form = CreateGameForm()
	if form.validate_on_submit():
		game = Game(user_id=form.user_id.data,gamename=form.gamename.data,descript=form.descript.data, game_lib=form.game_lib.data, example_code=form.example_code.data)
		db.session.add(game)
		db.session.commit()
		# current_game=game
		# print(current_game)
		# '''obj_to_json'''
		g_query=Game.query.filter_by(gamename=form.gamename.data).first()
		if isinstance(g_query, list):
			result = obj_to_json(g_query)
		elif getattr(g_query, '__dict__', ''):
			result = obj_to_json([g_query])
		else:
			result = {'result': g_query}
		game_result=json.dumps(result, cls=ComplexEncoder)
		# '''obj_to_json'''end

		flash('Congratulations, the game is created!')
		return redirect(url_for('games.open_room', gameObj=game_result))
	return render_template('games/create_game.html', title='Register', form=form)

@bp.route('/open_room', methods=['GET','POST'])
@login_required
def open_room():
	gameObj = request.args.get('gameObj')
	loadgame = json.loads(gameObj)
	lo0=loadgame[0]
	print('lolo[game_lib]: ',lo0['game_lib'])
	
	form = OpenRoomForm()
	if form.validate_on_submit():
		# room = Room(roomname=form.roomname.data, game_id=gameId, player_list=form.player_list.data)
		# db.session.add(room)
		# db.session.commit()
		# # current_room=room
		flash('Congratulations, now start the room!')
		# q_room=Room.query.filter_by(roomname=form.roomname.data).first()
		# return redirect(url_for('games.room_wait',room=room))
	return render_template('games/open_room.html', title='open_room',form=form)

@bp.route('/room_wait', methods=['GET','POST'])
@login_required
def room_wait(room):
	if is_all_in_room:
		return redirect(url_for('games.start_game',roomId=current_room.id))
	room_game = Game.query.filter_by(id=room.game_id).first()
	flash('Congratulations, now start the room!')
	return render_template('games/room_wait.html', title='room_wait',game_name=room_game.name,game_p_num =room_game.player_num,game_img = room_game.img)


@bp.route('/start_game/<int:gameId>', methods=['GET','POST'])
@login_required
def start_game(gameId):
	form = StartGameForm()
	if form.validate_on_submit():
		log = Log(game_id=gameId, user_id=form.user_id.data)
		db.session.add(log)
		db.session.commit()
		current_log=log.id
		flash('Congratulations, now start the game!')
		return redirect(url_for('games.game_view',logId=current_log))
	return render_template('games/start_game.html', title='Register', gameId=current_game,form=form)

# # @bp.route('/codes', methods=['GET','Comment'])
# # @login_required
# # def commit_code():

# # 	return render_template('games/commit_code.html', title='Commit Code',
# #                            form=form,codeId='01')
@bp.route('/game_view/<int:logId>', methods=['GET','POST'])
@login_required
def game_view(logId):

	return render_template('games/game_view.html')

@bp.route('/commit_code', methods=['GET','POST'])
@login_required
def commit_code():

	# name = session.get('name', '')
	# room = session.get('room', '')
	# if name == '' or room == '':
	# 		return redirect(url_for('.index'))
	editor_content = request.args.get('editor_content', 0, type=str)
	print(json.dumps({'selected post': str(editor_content)}))
	code = Code(log_id='1234', body=editor_content, commit_msg="fake commit_msg.data",game_id='12',user_id='12345')
	db.session.add(code)
	db.session.commit()
	flash('Your code have been saved.')
	current_code=code.id
	print('commit')
	ws = create_connection("ws://140.116.82.229:9000")
	print("Sending 'Hello, World'...")
	ws.send(json.dumps({'code':code.body,'room':'room','logId':current_log,'userId':'12345'}))
	print("Receiving...")
	result =  ws.recv()
	print("Received '%s'" % result)
	ws.close()

	return redirect(url_for('games.game_view',logId=current_log))

@bp.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = ChatForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.game_view',logId=current_log))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('games/index.html', form=form)

# @bp.route('/logs/<int:logId>',methods=['GET'])
# def get_game_result(logId): # in game view, replace commit_code

# 	if form.validate_on_submit():
# 		log = Log.query.filter_by(id=form.log_id.data).first()
# 		if log:
# 			flash('show log')
# 		else:
# 			flash('this round is deleted')
# 		return redirect(url_for('games.game_view'))
# 	return render_template('games/logs.html', title='Game Log',logId=current_log)

# @bp.route('/logs/<int:logId>', methods=['DELETE'])
# @login_required
# def unsave_log(token):
# 	log = Log.query.filter_by(id=form.log_id.data).first()
# 	db.session.delete(log)
# 	db.session.commit()
# 	flash('Your log has been deleted.')
# 	return render_template('games/logs.html', logId=current_logs)
