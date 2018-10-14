from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, StartGameForm,CommentCodeForm, OpenRoomForm, LoginForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Comment, Game, Log, Code, Comment,Room
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
	## test gameObj start
	gameObj = request.args.get('gameObj')
	loadgame = json.loads(gameObj)
	lo0=loadgame[0]
	print('lolo[game_lib]: ',lo0['game_lib'])
	## test gameObj end

	form = OpenRoomForm()
	if form.validate_on_submit():
		r_query=Room.query.filter_by(roomname=form.room_name.data).first()
		if r_query is None:
			room = Room(roomname=form.room_name.data, game_id=form.game_id.data, player_list=form.player_list.data,max_people=form.max_people.data)
			db.session.add(room)
			db.session.commit()
			session['game_id']=form.game_id.data
			session['room_id']=r_query.id
		else:
			print("please change name")

		if isinstance(r_query, list):
			result = obj_to_json(r_query)
		elif getattr(r_query, '__dict__', ''):
			result = obj_to_json([r_query])
		else:
			result = {'result': r_query}
		room_result=json.dumps(result, cls=ComplexEncoder)
		flash('Congratulations, now start the room!')
		return redirect(url_for('games.room_wait',form.game_id.data))
		# q_room=Room.query.filter_by(roomname=form.roomname.data).first()
		# return redirect(url_for('games.room_wait',room=room))
	elif request.method == 'GET':
		form.name.data = session.get('name', '')
        # form.room_id.data = session.get('room_id', '')
	return render_template('games/open_room.html', title='open_room',form=form)

@bp.route('/room_wait', methods=['GET','POST'])
@login_required
def room_wait():
	room_id=session.get('room_id')
	
	room=Room.query.filter_by(id=room_id).first()
	player_list=room.player_list.split(',')
	if current_user in player_list:
		player_list.remove(current_user)
		str_list=''.join(player_list)
		room.player_list=str_list
		db.session.commit()

	is_all_in_room =len(player_list)
	print(is_all_in_room)
    # form.room.data = session.get('room', '')
	print(current_room.id) #有效？
	gameId = request.args.get('gameId', 1, type=int)
	if is_all_in_room:
		return redirect(url_for('games.start_game',gameId))
	room_game = Game.query.filter_by(id=room.game_id).first()
	flash('Congratulations, now start the room!')
	return render_template('games/room_wait.html', title='room_wait',game_name=room_game.name,game_p_num =room_game.player_num,game_img = room_game.img)


@bp.route('/start_game/<int:gameId>', methods=['GET','POST'])
@login_required
def start_game(gameId):
	form = StartGameForm()
	if form.validate_on_submit():
		# game_id=session.get('game_id')
		log = Log(game_id=gameId)
		db.session.add(log)
		db.session.commit()
		current_log=log.id
		session['log_id'] =log.id
		flash('Congratulations, now start the game!')
		return redirect(url_for('games.game_view',logId=log.id))
	return render_template('games/start_game.html', title='Register', gameId=gameId,form=form)

# # @bp.route('/codes', methods=['GET','Comment'])
# # @login_required
# # def commit_code():

# # 	return render_template('games/commit_code.html', title='Commit Code',
# #                            form=form,codeId='01')
@bp.route('/game_view/<int:logId>', methods=['GET','POST'])
@login_required
def game_view(logId):

	comment_form = CommentCodeForm() #current_log.id
	name = session.get('name', '')
	room = session.get('room', '')

	if request.method == 'GET':

		if name == '' or room == '':
			return redirect(url_for('.index'))

		current_code=logId
		page = request.args.get('page', 1, type=int)
		comments = Comment.query.filter_by(code_id = current_code).order_by(Comment.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

		# next_url = url_for('games.game_view', page=comments.next_num, logId=current_log) \
		# if comments.has_next else None
		# prev_url = url_for('games.game_view',page = comments.prev_num, logId=current_log) \
		# if comments.has_prev else None
		# return render_template('games/game_view.html',logId=current_log, title='Commit Code',
        #                    comment_form=comment_form,comments=comments.items, name=name, room=room) #next_url=next_url, prev_url=prev_url

	elif comment_form.validate_on_submit():
		current_code=logId
		comment = Comment(code_id=current_code, body=comment_form.body.data)#comment_form.code_id.data
		db.session.add(comment)
		db.session.commit()
		flash('Your code have been saved.')
	return render_template('games/game_view.html',logId=current_log, title='Commit Code',
                           comment_form=comment_form, name=name, room=room)


@bp.route('/commit_code', methods=['GET','POST'])
@login_required
def commit_code():
	print("commit")
	name = session.get('name', '')
	room = session.get('room', '')# for gameserver to save exec code, not for db-code(no need to save room)  
	log_id = session.get('logId', '')
	# if name == '' or room == '':
	# 		return redirect(url_for('.index'))
	editor_content = request.args.get('editor_content', 0, type=str)
	commit_msg = request.args.get('commit_msg', 0, type=str)
	code = Code(log_id=log_id, body=editor_content, commit_msg=commit_msg,game_id=name,user_id=current_user.id)
	db.session.add(code)
	db.session.commit()
	flash('Your code have been saved.')
	current_code=code.id

	ws = create_connection("ws://localhost:6005")
	print("Sending 'Hello, World'...")
	ws.send(json.dumps({'code':editor_content,'room':room,'logId':name,'userId':current_user.id,'game_id':log_id}))
	print("Receiving...")
	result =  ws.recv()
	print("Received '%s'" % result)
	ws.close()
	
	return redirect(url_for('.game_view',logId=current_log))

@bp.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.game_view',logId=current_log))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        rooms = Room.query.order_by(Room.timestamp.desc()).all()
       


    return render_template('games/index/index.html', form=form, rooms=rooms)

@bp.route('/gameover/<logId>', methods=['GET','POST'])
@login_required
def gameover(logId):
	# winner_id
	# get record_content from gameserver or local var ?
	Log.query.filter_by(id=logId).update(dict(record_content='ooooo',score=300,winner_id=winner_id))
	log=Log.query.with_entities(Log.game_id).filter_by(id=logId).first()
	db.session.commit()
	form = LoginForm()
	print(Log.get_rank_list(Log,str(log[0])))# log[1]=game_id
	return render_template('games/index.html', title='Register',form=form)


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
