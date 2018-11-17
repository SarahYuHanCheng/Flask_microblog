from flask import session,redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio # //in microblog.py
from flask_login import current_user
from app.models import User, Game, Log, Code
from app import db

@socketio.on('connect', namespace='/test')
def new_connect():
    print("client connect")
    
@socketio.on('score',namespace = '/test') 
def game_over(message):
    # msg：tuple([l_score,r_score,gametime])??
    # 使 webserver切換至 gameover路由
    print('end game',message['msg'])
    return redirect(url_for('games.gameover',room= message['msg'][3],msg= message['msg']))

@socketio.on('connectfromgame',namespace = '/test')
def test_connect(message):
    # 接收來自 exec主機 gamemain傳送的訊息並再傳至browser
    # msg:??
    print(message['msg'])
    emit('gameobject', {'msg': message['msg']},room= message['msg'][3])

@socketio.on('join' ,namespace = '/test')
def joined(message):
    # 一個房間會有 n+1的連線數(n個 browser, 一個gamemain)
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    log_id = message['room'] #session.get('room') 
    join_room(log_id)
    l= Log.query.filter_by(id=log_id).first()
    print("log",l.privacy,l.status)
    if l.privacy is 1: # public,可以
        if l.status is not 0 : # room還沒滿,可以進來參賽(新增 player_in_log data, update user的 current_log) # if s is not (0 or 1) :
        
            game_player_num = Game.query.with_entities(Game.player_num).filter_by(id=l.game_id).first()
            print("l.current_users:",l.current_users)
            l.current_users.append( current_user )
            print("l.current_users after:",l.current_users)
            current_users_len = len(l.current_users)
            print('after append',current_users_len)
            l.status = int(game_player_num[0]) - current_users_len
            current_user.current_log_id = log_id
            db.session.commit()
            print("user in room: ",l.current_users)
            print('status:',l.status)
            if l.status is 0 :
                print("redirect to game_view")
                emit('arrived', {'msg': current_user.id},namespace = '/test',room= log_id)
                
            # 單純觀賽
        elif l.privacy is 2:# friend
            pass
        else:# only invited
            pass
   

@socketio.on('text' ,namespace = '/test')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left',namespace = '/test' )
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

