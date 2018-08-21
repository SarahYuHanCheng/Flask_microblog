# -----------------------------------------
# gamemain
# socketio server communicate to P1,P2
# socketio client communicate to webserver
# -----------------------------------------
import random
import socketio
import eventlet
import sys
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)

from socketIO_client import SocketIO, LoggingNamespace

WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
ball = [0, 0]
ball_vel = [0, 0]
paddle1_vel = 0
paddle2_vel = 0
l_score = 0
r_score = 0

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('P1')
def on_P1(sid, p1_vel):
    global paddle1_vel
    # print("P1 " , p1_vel)
    paddle1_vel=p1_vel
    game()

@sio.on('P2')
def on_P2(sid, p2_vel):
    global paddle2_vel
    paddle2_vel=p2_vel
    game()

@sio.on('disconnect')#, namespace='/chat'
def disconnect(sid):
    print('disconnect ', sid)

def ball_init(right):
    global ball, ball_vel
    ball = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(2, 4)
    vert = random.randrange(1, 3)

    if right == False:
        print("init move left")
        horz = - horz

    ball_vel = [horz, -vert]
def __init__():
    global paddle1, paddle2, paddle1_vel, paddle2_vel, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    paddle1 = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2 = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT //2]
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)

def score():
    pass

def game():
    play()
    send_to_Players()

def send_to_Players():
    sio.emit('gameinfo',{'msg':tuple([ball,paddle1[1],paddle2[1]])})

def send_to_webserver():
    with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
        socketIO.emit('connectfromgame',{'msg':tuple([ball,room,paddle1,paddle2])})

def end_game():
    print("end")
    score()
    sys.exit()

def play():
    global paddle1, paddle2,paddle1_vel,paddle2_vel, ball, ball_vel, l_score, r_score, cnt

    print('paddle[1,2]:(%d,%d)'%(paddle1[1],paddle2[1]))
    if paddle1[1] > HALF_PAD_HEIGHT and paddle1[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle1[1] += paddle1_vel
    elif paddle1[1] == HALF_PAD_HEIGHT and paddle1_vel > 0:
        paddle1[1] += paddle1_vel
    elif paddle1[1] == HEIGHT - HALF_PAD_HEIGHT and paddle1_vel < 0:
        paddle1[1] += paddle1_vel

    if paddle2[1] > HALF_PAD_HEIGHT and paddle2[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle2[1] += paddle2_vel
    elif paddle2[1] == HALF_PAD_HEIGHT and paddle2_vel > 0:
        paddle2[1] += paddle2_vel
    elif paddle2[1] == HEIGHT - HALF_PAD_HEIGHT and paddle2_vel < 0:
        paddle2[1] += paddle2_vel


    ball[0] += int(ball_vel[0])
    ball[1] += int(ball_vel[1])



    if int(ball[1]) <= BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]
    if int(ball[1]) >= HEIGHT + 1 - BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]


    if int(ball[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball[1]) in range(paddle1[1] - HALF_PAD_HEIGHT,
                                                                                 paddle1[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball[0]) <= BALL_RADIUS + PAD_WIDTH:
        r_score += 1
        print('r_score ',r_score)
        if r_score > 1:
            end_game()
        ball_init(True)

    if int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball[1]) in range(
            paddle2[1] - HALF_PAD_HEIGHT, paddle2[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
        l_score += 1
        print('l_score ',l_score)
        if l_score > 1:
            end_game()
        ball_init(False)


if __name__ == '__main__':
    __init__()
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
     