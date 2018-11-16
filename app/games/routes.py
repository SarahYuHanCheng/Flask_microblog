from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, ChooseGameForm,CommentCodeForm, AddRoomForm, LoginForm, JoinForm, LeaveForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Game, Log, Code
from werkzeug.urls import url_parse
from datetime import datetime
from app.games import bp, current_game, current_log, current_code, current_comment
from websocket import create_connection
import json, sys
from flask_socketio import emit

current_game = '3333'
# print(current_log)
class ComplexDecoder(json.JSONDecoder):
	# 目前還沒用到
	def default(obj):
		return json.JSONDecoder.default(obj)
class ComplexEncoder(json.JSONEncoder):
	# 解開query時用到
	def default(self, obj):
		import datetime
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)

def obj_to_json(obj_list):
	# query出來之後 轉 json
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
	# 新增遊戲
	form = CreateGameForm()
	if form.validate_on_submit():
		game = Game(user_id=form.user_id.data,gamename=form.gamename.data,descript=form.descript.data, player_num=form.player_num.data,category_id=form.category_id.data)
		# game = Game(user_id=form.user_id.data,gamename=form.gamename.data,descript=form.descript.data, game_lib=form.game_lib.data, example_code=form.example_code.data)
		db.session.add(game)
		db.session.commit()

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
		return redirect(url_for('games.add_room', gameObj=game_result))
	return render_template('games/create_game.html', title='Register', form=form)

@bp.route('/add_room', methods=['GET','POST'])
@login_required
def add_room():
	# 開房間, add log data with game,user
	add_form = AddRoomForm()
	if add_form.validate_on_submit():
		if add_form.privacy.data is 3:
			players = (add_form.players_status.data).split(',')
		else:
			game_player_num = Game.query.with_entities(Game.player_num).filter_by(id=add_form.game.data).first()
			players = game_player_num[0]
		log = Log(game_id=add_form.game.data,privacy=add_form.privacy.data,status=players)
		db.session.add(log)
		log.current_users.append(current_user)
		# 若是設定 privacy==friends(指定玩家), log.current_users.append((choose_form.player_list).split(','))
		db.session.commit()
		return redirect(url_for('games.room_wait',log_id=log.id))

	return render_template('games/room/add_room.html', title='add_room',form=add_form)

@bp.route('/room_wait/<int:log_id>', methods=['GET','POST'])
@login_required
def room_wait(log_id):
	# client 進來後, check log/status, 若沒有 add player_in_log,  
	# 等待玩家到齊就能 start game,''' 按下 btn('start game')''',切換到 game_view 
	# check log/privacy
	join_form = JoinForm()
	if request.method == 'GET':
		return render_template('games/room/room_wait.html', title='room_wait',join_form=join_form) #,game_name=room_game.name,game_p_num =room_game.player_num,game_img = room_game.img
	else:
		l= Log.query.filter_by(id=log_id).first()
		
		# leave_form = LeaveForm()
		# choose_form = ChooseGameForm()

		print('wait_room',l.privacy,l.status)
		if l.privacy is 1: # public,可以
			if l.status is not 0 : # room還沒滿,可以進來參賽(新增 player_in_log data, update user的 current_log) # if s is not (0 or 1) :
				if join_form.validate_on_submit():# 按下參賽按鈕
					
					
					game_player_num = Game.query.with_entities(Game.player_num).filter_by(id=l.game_id).first()
					l.current_users.append( current_user )
					current_users_len = len(l.current_users)
					l.status = int(game_player_num[0]) - current_users_len
					current_user.current_log_id = log_id
					db.session.commit()
					print("user in room: ",l.current_users)
					print('status:',l.status)
					if l.status is 0 :
						print("redirect to game_view")
						emit('start', {'msg': 'start'},room= l.id)
						return redirect(url_for('games.game_view',log_id=l.id))
					else:
						return redirect(url_for('games.room_wait',log_id=l.id))
					
				# elif leave_form.validate_on_submit():
				# 	# 按下取消,退賽按鈕
				# 	l.current_users.remove( current_user )
				# 	current_user.current_log_id = ""
				# 	db.dession.commit()
				# 	print("leave")
				# 	return redirect(url_for('games.index'))

					# 單純觀賽
		elif l.privacy is 2:# friend
			pass
		else:# only invited
			pass


@bp.route('/game_view/<int:log_id>', methods=['GET','POST'])
@login_required
def game_view(log_id):
	# 比賽畫面
	comment_form = CommentCodeForm() #current_log.id
	name = session.get('name', '')
	room = session.get('room', '')
	print("logId",log_id)
	log_id = session.get('log_id', '')
	print("log_id",log_id)

	if request.method == 'GET':
		print("log_id",log_id)
		if name == '' or room == '':
			return redirect(url_for('.index'))

		current_code=log_id
		page = request.args.get('page', 1, type=int)
		# comments = Comment.query.filter_by(code_id = current_code).order_by(Comment.timestamp.desc()).paginate(
		# page, current_app.config['POSTS_PER_PAGE'], False)

		# next_url = url_for('games.game_view', page=comments.next_num, logId=current_log) \
		# if comments.has_next else None
		# prev_url = url_for('games.game_view',page = comments.prev_num, logId=current_log) \
		# if comments.has_prev else None
		# return render_template('games/game_view.html',logId=current_log, title='Commit Code',
		#					comment_form=comment_form,comments=comments.items, name=name, room=room) #next_url=next_url, prev_url=prev_url
		return render_template('games/game/game_view.html',log_id=current_log, title='Commit Code',
						   comment_form=comment_form, name=name, room=room,box_res="default")
		
	elif comment_form.validate_on_submit():
		current_code=log_id
		# comment = Comment(code_id=current_code, body=comment_form.body.data)#comment_form.code_id.data
		# db.session.add(comment)
		# db.session.commit()
		flash('Your code have been saved.')
	else:
		print(request.method)
		if request.args.get('box_res') :
			box_res = request.args.get('box_res')
			print("res ok",box_res)
		else: 
			box_res='defult'
			print("res no")
		return render_template('games/game/game_view.html',logId=current_log, title='Commit Code',
						   comment_form=comment_form, name=name, room=room,box_res=box_res)
		
@bp.route('/commit_code', methods=['GET','POST'])
@login_required
def commit_code():
	# 用ws 提交程式碼給 gameserver
	print("commit")
	name = session.get('name', '')
	room = session.get('room', '')# for gameserver to save exec code, not for db-code(no need to save room)  
	log_id = session.get('log_id', '')
	game_id = session.get('game_id', '')

	editor_content = request.args.get('editor_content', 0, type=str)
	commit_msg = request.args.get('commit_msg', 0, type=str)
	code = Code(log_id=log_id, body=editor_content, commit_msg=commit_msg,game_id=game_id,user_id=current_user.id)
	db.session.add(code)
	db.session.commit()

	l=Log.query.filter_by(id=1).first()
	players = l.current_users

	player_list=[]
	print("players: ",players)
	for i,player in enumerate(players):
		print("type:",type(player.id),type(current_user.id))
		if player.id == current_user.id:
			players.pop(i)
			l.current_users=players
			print("in condition,,,players_list: ",players)
			db.session.commit()
		else:
			player_list.append(player.id)
	ws = create_connection("ws://localhost:6005")
	ws.send(json.dumps({'from':'webserver','code':editor_content,'log_id':1,'user_id':current_user.id,'category_id':1,'game_id':1,'language':"python",'player_list':player_list}))
	# ws.send(json.dumps({'from':'webserver','code':editor_content,'room_name':room,'logId':name,'user_id':current_user.id,'game_lib_id':game_lib_id,'language':"python",'player_list':[1,2]}))
	# result =  ws.recv() #
	result="www"
	# print("Received '%s'" % result)
	ws.close()
	
	return redirect(url_for('games.game_view',log_id=current_log,box_res=result))

@bp.route('/', methods=['GET', 'POST'])
def index():
	# 主畫面會有很多tab(News, NewsGame, HotGames,Discuss, Rooms)
	"""Login form to enter a room."""
	print("user:",session.get('username','nnnooo'))
	form = LoginForm()
	if form.validate_on_submit():
		session['name'] = form.name.data
		session['room'] = form.room.data

		return redirect(url_for('.game_view',log_id=current_log))
	elif request.method == 'GET':
		form.name.data = session.get('name', '')
		form.room.data = session.get('room', '')
		wait_rooms = Log.query.filter(Log.game_id>0).order_by(Log.timestamp.desc()).all()
		gaming_room = Log.query.filter(Log.game_id==0).order_by(Log.timestamp.desc()).all()
		# rooms = Room.query.order_by(Room.timestamp.desc()).all()
		
	   
	return render_template('games/index/index.html', form=form,wait_rooms=wait_rooms,gaming_room=gaming_room)

@bp.route('/gameover/<log_id>', methods=['GET','POST'])
@login_required
def gameover(log_id):
	# event.py收到gameserver的 'score'訊息後, redirect到此遊戲結束的 route, update log, 顯示分數
	# get record_content from gameserver or local var ?
	# record display in many jpeg 為學習影像處理存擋, 也用來做回顧播放
	Log.query.filter_by(id=log_id).update(dict(record_content=msg[1],score=msg[2],winner_id=msg[3]))
	# Log.query.filter_by(id=logId).update(dict(record_content='ooooo',score=300,winner_id=winner_id))
	log=Log.query.with_entities(Log.game_id).filter_by(id=log_id).first()
	db.session.commit()
	print(Log.get_rank_list(Log,str(log[0])))# log[1]=game_id
	return render_template('games/index.html', title='Register')
