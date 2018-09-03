# -----------------------------------------
# gamemain
# socketio server communicate with P1,P2
# socketio client communicate with webserver
# -----------------------------------------
import random, math
import socketio
import eventlet
import sys,time, threading
from flask import Flask, render_template
# async_mode = None

sio = socketio.Server(async_handlers=True)
app = Flask(__name__)  


from socketIO_client import SocketIO, LoggingNamespace

WIDTH = 800
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = math.ceil(HEIGHT/3)
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
ball = [0, 0]
ball_vel = [0, 0]
paddle1_move = 0
paddle2_move = 0
l_score = 0
r_score = 0
barrier=2 # ensure a round fair
cnt=0
p1_timeout=0.0001
p2_timeout=0.0001
start=0 # control timeout loop

# eventlet.monkey_patch()

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('P1_in')
def on_P1_in(sid):
    global barrier,start
    barrier-=1
    if barrier>0:
        sio.emit("wait")
    else:
        send_to_Players('gameinfo')
        print('%f'%time.clock())
        start=1
        # eventlet.spawn(action)

@sio.on('P2_in')
def on_P1_in(sid):
    global barrier,start
    barrier-=1    
    if barrier>0:
        sio.emit("wait")
    else:
        send_to_Players('gameinfo')
        print('%f'%time.clock())
        start=1
        # eventlet.spawn(action)

@sio.on('P1')
def on_P1(sid, msg):
    global paddle1_move,barrier,p1_timeout
    print('cnt ',msg['cnt'])
    paddle1_move=msg['paddle_vel']
    print('P1 ',paddle1_move)
    p1_timeout=time.clock()
    barrier-=1
    if barrier==0:
        send_to_webserver()
        game()

@sio.on('P2')
def on_P2(sid, msg):
    global paddle2_move,barrier,p2_timeout
    paddle2_move=msg['paddle_vel']
    print('P2 ',paddle2_move)
    p2_timeout=time.clock()
    barrier-=1
    if barrier==0:
        send_to_webserver()
        game()


@sio.on('disconnect')#, namespace='/chat'
def disconnect(sid):
    print('disconnect ', sid)
    return

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
    global paddle1, paddle2, paddle1_move, paddle2_move, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    print('PAD_HEIGHT ',PAD_HEIGHT)
    print('HALF_PAD_HEIGHT ',HALF_PAD_HEIGHT)
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
    try:
        play()
    except:
        return
    send_to_Players('gameinfo')

def send_to_Players(instr):
    print('send_to_Players')
    global serversock,cnt,barrier
    if (instr == 'gameinfo') and barrier==0:
        cnt+=1
        msg={'msg':tuple([ball,paddle1[1],paddle2[1],cnt])}
        sio.emit(instr,msg)
        print('emit cnt ',cnt)
        barrier=2
    elif instr == 'endgame':
        msg={'msg':ball}
        sio.emit(instr,msg)
        print('endgame %f'%time.clock()) 

def send_to_webserver():
    global ball,paddle1,paddle2
    with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
        socketIO.emit('connectfromgame',{'msg':tuple([ball,paddle1,paddle2])})

    

def play():
    try:
        global paddle1, paddle2,paddle1_move,paddle2_move, ball, ball_vel, l_score, r_score, cnt
        global barrier
        print('ball_play: ',ball)
        
        if paddle1[1] > HALF_PAD_HEIGHT and paddle1[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle1[1] += paddle1_move
            print('p1 normal')
        elif paddle1[1] <= HALF_PAD_HEIGHT and paddle1_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            print('p1 top')
        elif paddle1[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle1_move < 0:
            paddle1[1] = HEIGHT - HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            print('p1 bottom')
        else:
            print('p2 else')

        if paddle2[1] > HALF_PAD_HEIGHT and paddle2[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle2[1] += paddle2_move
            print('p2 normal')
        elif paddle2[1] <= HALF_PAD_HEIGHT and paddle2_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            print('p2 top')
        elif paddle2[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle2_move < 0:
            paddle1[1] =HEIGHT- HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            print('p2 bottom')
        else:
            print('p2 else')

        print('paddle:(%d,%d)'%(paddle1[1],paddle2[1]))

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
            
            if r_score < 1:
                ball_init(True)
            else:
                barrier=1
                send_to_Players('endgame')
                print('ball ',ball)

        if int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball[1]) in range(
                paddle2[1] - HALF_PAD_HEIGHT, paddle2[1] + HALF_PAD_HEIGHT, 1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
            l_score += 1
            print('l_score ',l_score)
            
            if l_score < 1:
                ball_init(False)
                
            else:
                barrier=1
                send_to_Players('endgame')
                print('ball ',ball)

    except(RuntimeError, TypeError, NameError):
        # raise SystemExit
        print('play except')
        return

    

def serve_app(_sio, _app):
    app = socketio.Middleware(_sio, _app)
    serversock=eventlet.wsgi.server(eventlet.listen(('', 8000)), app) 

def action() :
    global p1_timeout, p2_timeout,barrier, paddle1_move, paddle2_move, start
    while True:
        if start==1:
            time.sleep(0.01)
            # print('action ! -> time : {:.1f}s'.format(time.time()-StartTime))
            print('p1_timeout ',p1_timeout)
            print('p2_timeout ',p2_timeout)
            print('time.clock()-p1_timeout ',time.clock()-p1_timeout)
            print('time.clock()-p2_timeout ',time.clock()-p2_timeout)
            
            if (time.clock()-p1_timeout)>0.025:
                print('p1_timeout_')
                
                if p1_timeout<=p2_timeout:
                    # print('p1_timeout')
                    paddle1_move=0
                    barrier=0
                    p1_timeout=time.clock()
                    p2_timeout=time.clock()
                    game()
                elif p1_timeout>p2_timeout:
                    # print('p2_timeout')
                    paddle2_move=0
                    barrier=0
                    p1_timeout=time.clock()
                    p2_timeout=time.clock()
                    game()
            elif (time.clock()-p2_timeout)>0.025:
                print('p2_timeout_')
                if p1_timeout<=p2_timeout:
                    # print('p1_timeout')
                    paddle1_move=0
                    barrier=2
                    p1_timeout=time.clock()
                    p2_timeout=time.clock()
                    game()
                elif p1_timeout>p2_timeout:
                    # print('p2_timeout')
                    paddle2_move=0
                    barrier=2
                    p1_timeout=time.clock()
                    p2_timeout=time.clock()
                    game()

        
if __name__ == '__main__':
    __init__()

    wst = threading.Thread(target=serve_app, args=(sio,app))
    wst.daemon = True
    wst.start()

    StartTime=time.time()
    

timeout= threading.Thread(target=action)
timeout.start()
# class setInterval :
#     def __init__(self,interval,action) :
#         self.interval=interval
#         self.action=action
#         self.stopEvent=threading.Event()
#         thread=threading.Thread(target=self.__setInterval)
#         thread.start()

#     def __setInterval(self) :
#         nextTime=time.time()+self.interval
#         while not self.stopEvent.wait(nextTime-time.time()) :
#             nextTime+=self.interval
#             self.action()

#     def cancel(self) :
#         self.stopEvent.set()

# # # start action every 0.6s
# inter=setInterval(0.01,action)
# print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# # # will stop interval in 5s
# t=threading.Timer(25,inter.cancel)
# t.start()
