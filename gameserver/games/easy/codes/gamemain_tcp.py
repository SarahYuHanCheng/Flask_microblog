import socket,json,time
import threading,math, random

bind_ip = '127.0.0.1'
bind_port = 8000


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print('Listening on {}:{}'.format(bind_ip, bind_port))

playerlist = []

WIDTH = 800
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = math.ceil(HEIGHT)
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
ball = [0, 0]
ball_vel = [0, 0]
paddle1_move = 0
paddle2_move = 0
l_score = 0
r_score = 0
barrier=[0,0] # ensure a round fair
cnt=0
p1_rt=0.0001
p2_rt=0.0001
start=0 # control timeout loop

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

def send_to_webserver():
    global ball,paddle1,paddle2

def send_to_Players(instr):

    global serversock,cnt,barrier
    print('send_to_Players barrier', barrier)

    if (instr == 'gameinfo') and barrier==[1,1]:
        cnt+=1
        msg={'msg':tuple([ball,paddle1[1],paddle2[1],cnt])}
        # sio.emit(instr,msg)
        print('emit cnt ',cnt)
        
    elif instr == 'endgame':
        msg={'msg':ball}
        # sio.emit(instr,msg)
        print('endgame %f'%time.time()) 
    barrier=[0,0]


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
            print('p1 else')

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
                # barrier=1
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
                # barrier=1
                send_to_Players('endgame')
                print('ball ',ball)

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
    cnt=0
    while True:
        request = client_socket.recv(1024)
        # print('Received {}'.format(request))
        msg = json.loads(request)

        if msg['type']=='info':
            # print('info')
            if msg['who']=='P1':
                print('P1 content',msg['content'])
                paddle1_move=msg['content']
                p1_rt=time.time()
                barrier[0]=1
                if barrier[1]==1:
                    # send_to_webserver()
                    # game('on_p1')
                    cnt+=1
                    for cli in range(0,len(playerlist)):
                        playerlist[cli].send(str(msg['content']).encode())
                    barrier=[0,0]

            elif msg['who']=='P2':
                # print('P2 content',msg['content'])
                paddle2_move=msg['content']
                p2_rt=time.time()
                barrier[1]=1
                if barrier[0]==1:
                    # send_to_webserver()
                    # game('on_p2')
                    cnt+=1
                    for cli in range(0,len(playerlist)):
                        playerlist[cli].send(str(msg['content']).encode())
                    barrier=[0,0]

        elif msg['type']=='connect':
            
            if msg['who']=='P1':
                print('P1 in',barrier)
                barrier[0]=1
                if barrier[1]==1:
                	print("p1_start")
                	start=1
                	barrier=[0,0]
                
            elif msg['who']=='P2':
                print('P2 in',barrier)
                barrier[1]=1
                if barrier[0]==1:
                	print("p1_start")
                	start=1
                	barrier=[0,0]

        elif msg['type']=='disconnect':
            if msg['who']=='P1':
                print('P1 leave',cnt)
                # client_socket.close()
            elif msg['who']=='P2':
                print('P2 leave',cnt)
                # client_socket.close()

        
        # client_socket.close()

def serve_app():
    while True:
        client_sock, address = server.accept()
        playerlist.append(client_sock)
        # print ('[%i users online]\n' % len(playerlist))
        # print(playerlist)
        print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()

def timeout_check():
    print("call timeout")
    global p1_rt, p2_rt,barrier, paddle1_move, paddle2_move, start,playerlist
    # time.sleep(5)
    timeout=0.1
    while True:
        
        time.sleep(0.003)
        if start==1:
            print("check")
            if barrier[0]==0:
                p1_rt_sub=time.time()-p1_rt
                # print('p1_rt_sub %f p2_rt_sub %f, barrier '%(p1_rt_sub,time.time()-p2_rt)+str(barrier))
                
                if p1_rt_sub>timeout:
                    if barrier[1]==0:
                        timeout+=0.005    
                        print('p2 also no response, timeout increase: ',timeout)
                    

                    paddle1_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    # send_to_webserver()
                    # game('p1_timeout')
                    for cli in range(0,len(playerlist)):
                        playerlist[cli].send(b'111')
                    barrier=[0,0]

                    time.sleep(0.01)
                            
            elif barrier[1]==0:
                print('p2_no')
                if (time.time()-p2_rt)>timeout:
                    print('p2_rt',time.time()-p2_rt)
                    paddle2_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    # send_to_webserver()
                    # game('p2_timeout')
                    for cli in range(0,len(playerlist)):
                        playerlist[cli].send(b'222')
                    barrier=[0,0]
                    time.sleep(0.01)


if __name__ == '__main__':
    __init__()

    wst = threading.Thread(target=serve_app)
    wst.daemon = True
    wst.start()
    # wst.join()
    timeout= threading.Thread(target=timeout_check)
    timeout.start()
    # StartTime=time.time()/
    

