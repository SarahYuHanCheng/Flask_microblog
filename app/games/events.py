from flask import session,redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

@socketio.on('score') 
def game_over(message):
    # msg：tuple([l_score,r_score,gametime])??
    # 使 webserver切換至 gameover路由
    print('end game',message['msg'])
    return redirect(url_for('games.gameover',room= message['msg'][3],msg= message['msg']))

@socketio.on('connectfromgame')
def test_connect(message):
    # 接收來自 exec主機 gamemain傳送的訊息並再傳至browser
    # msg:??
    global cnt
    cnt+=1
    print(cnt)
    emit('gameobject', {'msg': message['msg']},room= message['msg'][3])

@socketio.on('joined' )
def joined(message):
    # 一個房間會有 n+1的連線數(n個 browser, 一個gamemain)
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text' )
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left' )
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

