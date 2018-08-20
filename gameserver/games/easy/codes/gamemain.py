# -----------------------------------------
# gamemain
# socketio server communicate to P1,P2
# socketio client communicate to webserver
# -----------------------------------------
import socketio
import eventlet
import pingpong
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)

from socketIO_client import SocketIO, LoggingNamespace

ball=[5,6]
paddle1=[3]
paddle2=[8]

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('P1')
def print_message(sid, message):
    print("P1 Socket ID: " , sid)
    game(message)

@sio.on('P2')
def print_message(sid, message):
    print("P2 Socket ID: " , sid)
    game(message)

@sio.on('disconnect')#, namespace='/chat'
def disconnect(sid):
    print('disconnect ', sid)

def __init__():
    pass

def score():
    pass

def game(result):
    print("call game:",result)
    send_to_Players()

def send_to_Players():
    sio.emit('gameinfo',{'msg':tuple([ball,paddle1,paddle2])})

def send_to_webserver():
    with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
        socketIO.emit('connectfromgame',{'msg':tuple([ball_pos,room,paddle1_pos,paddle2_pos])})



if __name__ == '__main__':
     app = socketio.Middleware(sio, app)
     eventlet.wsgi.server(eventlet.listen(('', 8000)), app)