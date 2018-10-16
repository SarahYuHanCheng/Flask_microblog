from flask import session,redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

# @socketio.on('my event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data']})

# @socketio.on('my broadcast event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('endgame') # tuple([l_score,r_score,gametime])
def game_over(message):
    print('end game',message['msg'])
    # emit('gameresult', {'msg': message['msg']},room='q1')
    return redirect(url_for('games.gameover',logId= message['msg'][3]))
cnt=0
@socketio.on('connectfromgame')
def test_connect(message):
    global cnt
    cnt+=1
    print(cnt)
    emit('gameobject', {'msg': message['msg']},room='q1')

# @socketio.on('disconnect', namespace='/test')
# def test_disconnect():
#     print('Client disconnected')

@socketio.on('joined' )
def joined(message):
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

