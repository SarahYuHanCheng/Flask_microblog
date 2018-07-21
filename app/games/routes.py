from flask import render_template, flash, redirect, url_for, request
from app import db
from app.games.forms import CreateGameForm, StartGameForm, CommitCodeForm,CommentCodeForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Post, Game, Log, Code
from werkzeug.urls import url_parse
from datetime import datetime
from app.games import bp, current_game, current_log, current_code

current_game = '3333'
print(current_game)
print(current_log)
@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
	form = CreateGameForm()
	if form.validate_on_submit():
		game = Game(user_id=form.user_id.data,descript=form.descript.data, game_lib=form.game_lib.data, example_code=form.example_code.data)
		db.session.add(game)
		db.session.commit()
		flash('Congratulations, the game is created!')
		return redirect(url_for('games.start_game'))
	return render_template('games/register.html', title='Register', form=form)

@bp.route('/start_game', methods=['GET','POST'])
@login_required
def start_game():
	form = StartGameForm()
	if form.validate_on_submit():
		log = Log(game_id=form.game_id.data, user_id=form.user_id.data)
		db.session.add(log)
		db.session.commit()
		flash('Congratulations, now start the game!')
		return redirect(url_for('games.game_view'))
	return render_template('games/start_game.html', title='Register', form=form)

@bp.route('/codes', methods=['GET','POST'])
@login_required
def commit_code():
	form = CommitCodeForm() #current_log.id
	if form.validate_on_submit():
		code = Code(log_id=form.log_id.data, body=form.body.data, commit_msg=form.commit_msg.data)
		db.session.add(code)
		db.session.commit()
		flash('Your code have been saved.')
		return redirect(url_for('games.game_view',logId='01')) #不重新整理頁面
	elif request.method == 'GET':
		form.body.data = current_log#current_log.code
		form.commit_msg.data = current_log#current_log.commit_msg
	return render_template('games/commit_code.html', title='Commit Code',
                           form=form,codeId='01')
@bp.route('/game_view/<logId>', methods=['GET','POST'])
@login_required
def game_view(codeId):
	
	return render_template('games/game_view.html', title='Commit Code',
                           form=form)
@bp.route('/codes/<codeId>', methods=['GET','POST'])
@login_required
def comment_code(codeId):
	form = CommentCodeForm() #current_log.id
	if form.validate_on_submit():
		comment = Comment(code_id=form.code_id.data, body=form.body.data)
		db.session.add(code)
		db.session.commit()
		flash('Your code have been saved.')
		# return redirect(url_for('game.start_game')) #不重新整理頁面
	# elif request.method == 'GET':
	return render_template('games/comment_code.html', title='Commit Code',
                           form=form)
@bp.route('/logs/<logId>',methods=['GET'])
def get_game_result(logId): # in game view, replace commit_code
	
	if form.validate_on_submit():
		log = Log.query.filter_by(id=form.log_id.data).first()
		if log:
			flash('show log')
		else:
			flash('this round is deleted')
		return redirect(url_for('games.game_view'))
	return render_template('games/logs.html', title='Game Log',logId=current_log)

@bp.route('/logs/<logId>', methods=['DELETE'])
@login_required
def unsave_log(token):
	log = Log.query.filter_by(id=form.log_id.data).first()
	db.session.delete(log)
	db.session.commit()
	flash('Your log has been deleted.')
	return render_template('games/logs.html', logId=current_logs)
