from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, StartGameForm, CommitCodeForm,CommentCodeForm, LoginForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Comment, Game, Log, Code, Comment
from werkzeug.urls import url_parse
from datetime import datetime
from app.games import bp, current_game, current_log, current_code, current_comment
from websocket import create_connection
import json

current_game = '3333'
# print(current_log)
@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
	form = CreateGameForm()
	if form.validate_on_submit():
		game = Game(user_id=form.user_id.data,gamename=form.gamename.data,descript=form.descript.data, game_lib=form.game_lib.data, example_code=form.example_code.data)
		db.session.add(game)
		db.session.commit()
		current_game=game.id
		print(current_game)
		flash('Congratulations, the game is created!')
		return redirect(url_for('games.start_game', gameId=current_game))
	return render_template('games/create_game.html', title='Register', form=form)

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
	name = session.get('name', '')
	room = session.get('room', '')
	if name == '' or room == '':
			return redirect(url_for('.index'))
	editor_content = request.args.get('editor_content', 0, type=str)
	print(json.dumps({'selected post': str(editor_content)}))
	code = Code(log_id='1234', body=editor_content, commit_msg="fake commit_msg.data",game_id='12',user_id='12345')
	db.session.add(code)
	db.session.commit()
	flash('Your code have been saved.')
	current_code=code.id
	ws = create_connection("ws://localhost:6005")
	print("Sending 'Hello, World'...")
	ws.send(json.dumps({'code':code.body,'room':room,'logId':current_log,'userId':'12345'}))
	print("Receiving...")
	result =  ws.recv()
	print("Received '%s'" % result)
	ws.close()

	return redirect(url_for('games.game_view',logId=current_log))

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
