#gamemain
import socket,json,time
import threading,math, random, sys
from socketIO_client import SocketIO, LoggingNamespace
from websocket import create_connection

logId=sys.argv[1]
print('logId ',logId)
bind_ip = '127.0.0.1'
bind_port = 8800


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print('Listening on {}:{}'.format(bind_ip, bind_port))

playerlist = []

WIDTH = 800
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = math.ceil(HEIGHT/3)
HALF_PAD_WIDTH = PAD_WIDTH // 3
HALF_PAD_HEIGHT = PAD_HEIGHT // 3
ball = [0, 0]
ball_vel = [0, 0]
paddle1_move = 0
paddle2_move = 0
l_score = 0
r_score = 0
score={'type':'score','roomId':1,'l_score':0,'r_score':0}
barrier=[0,0] # ensure a round fair
cnt=0
p1_rt=0.0001
p2_rt=0.0001
start=0 # control timeout loop
lock = threading.Lock()

socketIO=SocketIO('127.0.0.1', 5000, LoggingNamespace)

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


def send_to_webserver(msg_type):
    print("web")
    lock.acquire()
    print("after lock")
    global ball,paddle1,paddle2,socketIO, score
    if msg_type=='info':
        socketIO.emit('connectfromgame',{'msg':tuple([ball,paddle1,paddle2])})
        lock.release()
    else:
        socketIO.emit('score',{'msg':score})
        lock.release()

def send_to_gameserver(score_msg):
    global logId
    print('gameserver')
    ws = create_connection("ws://localhost:6005")
    ws.send(json.dumps({'from':"game",'logId':logId,'score_msg':score_msg}))
    ws.close()
    exit()
    quit()
    

def send_to_Players(instr):

    global cnt,barrier,ball,paddle1,paddle2
    

    if (instr == 'gameinfo') and barrier==[1,1]:
        cnt+=1
        msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],cnt])}
        print('send_to_Players ', msg)
        for cli in range(0,len(playerlist)):
            playerlist[cli].send(json.dumps(msg).encode())
        barrier=[0,0]
        
    elif instr == 'gameover':
        msg={'type':'gameover'}
        for cli in range(0,len(playerlist)):
            playerlist[cli].send(json.dumps(msg).encode())
        barrier=[0,0]
        print('endgame %f'%time.time())
    else:
        return
    barrier=[0,0]


def play():
    try:
        global paddle1, paddle2,paddle1_move,paddle2_move, ball, ball_vel, l_score, r_score, cnt
        global barrier
        # print('ball_play: ',ball)
        lock.acquire()
        if paddle1[1] > HALF_PAD_HEIGHT and paddle1[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle1[1] += paddle1_move
            # print('p1 normal')
        elif paddle1[1] <= HALF_PAD_HEIGHT and paddle1_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            # print('p1 top')
        elif paddle1[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle1_move < 0:
            paddle1[1] = HEIGHT - HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            # print('p1 bottom')
        else:
            print('p1 else')

        if paddle2[1] > HALF_PAD_HEIGHT and paddle2[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle2[1] += paddle2_move
            # print('p2 normal')
        elif paddle2[1] <= HALF_PAD_HEIGHT and paddle2_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            # print('p2 top')
        elif paddle2[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle2_move < 0:
            paddle1[1] =HEIGHT- HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            # print('p2 bottom')
        else:
            print('p2 else')

        # print('paddle:(%d,%d,%d)'%(paddle1[1],paddle2[1],ball[0]))

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
                # barrier=1
                send_to_Players('gameover')
                print('ball ',ball)
                ball_init(False)

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
                # barrier=1
                send_to_Players('gameover')
                print('ball ',ball)
                ball_init(True)
        else:
            print("else")
        lock.release()
    except(RuntimeError, TypeError, NameError):
        # raise SystemExit
        print('play except')
        return
    

def game(where):
    try:
        print(where)
        play()
    except:
        return
    send_to_Players('gameinfo')

def handle_client_connection(client_socket):
    global paddle1_move,barrier,p1_rt,paddle2_move,p2_rt, playerlist, start
    client_socket.send(b'connectserver')
    
    while True:
        try:
            request = client_socket.recv(1024)
            # print('Received {}'.format(request))
            msg = json.loads(request)

            if msg['type']=='info':
                # print('info')
                if msg['who']=='P1':
                    # print('P1 content',msg['content'])
                    paddle1_move=msg['content']
                    p1_rt=time.time()
                    lock.acquire()
                    try:
                        barrier[0]=1
                        if barrier[1]==1:
                            lock.release()
                            send_to_webserver(msg['type'])
                            game('on_p1')
                    finally:
                        lock.release()
                        
                elif msg['who']=='P2':
                    # print('P2 content',msg['content'])
                    paddle2_move=msg['content']
                    p2_rt=time.time()
                    lock.acquire()
                    try:
                        barrier[1]=1
                        if barrier[0]==1:
                            lock.release()
                            send_to_webserver(msg['type'])
                            game('on_p2')
                    finally:
                        lock.release()

            elif msg['type']=='connect':
                
                if msg['who']=='P1':
                    print('P1 in',barrier)
                    p1_rt=time.time()
                    lock.acquire()
                    try:
                        barrier[0]=1
                        if barrier[1]==1:
                            print("p1_start")
                            start=1
                            send_to_Players("gameinfo")
                    finally:
                        lock.release()
                    
                elif msg['who']=='P2':
                    print('P2 in',barrier)
                    p2_rt=time.time()
                    lock.acquire()
                    try:
                        barrier[1]=1
                        if barrier[0]==1:
                            print("p2_start")
                            start=1
                            send_to_Players("gameinfo")
                    finally:
                        lock.release()
            elif msg['type']=='score':
                if msg['who']=='P1':
                    score['l_score']=msg['score']
                    print('P1 score',cnt)
                    lock.acquire()
                    try:
                        barrier[0]=1
                        if barrier[1]==0:
                            client_socket.close()
                            send_to_webserver('gameover')
                            send_to_gameserver(score)
                    finally:
                        lock.release()
                        

                    # client_socket.close()
                elif msg['who']=='P2':
                    print('P2 score',cnt)
                    score['r_score']=msg['score']
                    lock.acquire()
                    try:
                        barrier[1]=1
                        if barrier[0]==1:
                            client_socket.close()
                            send_to_webserver('gameover')
                            send_to_gameserver(score)
                    finally:
                        lock.release()
                    # client_socket.close()

            elif msg['type']=='disconnect':
                if msg['who']=='P1':
                    print('P1 leave',cnt)
                    # client_socket.close()
                elif msg['who']=='P2':
                    print('P2 leave',cnt)
                    # client_socket.close()
        except(RuntimeError, TypeError, NameError): 
            sys.exit()
    

        
        # client_socket.close()

def serve_app():
    while True:
        client_sock, address = server.accept()
        playerlist.append(client_sock)
        # print ('[%i users online]\n' % len(playerlist))
        # print(playerlist)
        # print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()

def timeout_check():
    global p1_rt, p2_rt,barrier, paddle1_move, paddle2_move, start,playerlist
    
    timeout=0.1
    # while True:
        
        # time.sleep(0.3)   
    if start==1:
        # print("check")
        lock.acquire()
        try:
            if barrier[0]==0:
                p1_rt_sub=time.time()-p1_rt
                # print('p1_rt_sub %f p2_rt_sub %f, barrier '%(p1_rt_sub,time.time()-p2_rt)+str(barrier))
                if p1_rt_sub>timeout:
                    if barrier[1]==0:
                        timeout+=0.005    
                        # print('p2 also no response, timeout increase: ',timeout)
                    paddle1_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    send_to_webserver('timeout')
                    game('p1_timeout')
                    
    
            elif barrier[1]==0:
                # print('p2_no')
                if (time.time()-p2_rt)>timeout:
                    # print('p2_rt',time.time()-p2_rt)
                    paddle2_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    send_to_webserver('timeout')
                    game('p2_timeout')
                    
        finally:
            lock.release()
            


if __name__ == '__main__':
    __init__()

    wst = threading.Thread(target=serve_app)
    wst.daemon = True
    wst.start()
    wst.join()
    # timeout= threading.Thread(target=timeout_check)
    # timeout.start()
    StartTime=time.time()
    

class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()

# # start action every 0.6s
inter=setInterval(0.03,timeout_check)
print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# # will stop interval in 5s
t=threading.Timer(90,inter.cancel)
t.start()
