import socket,json,time
import threading,math

bind_ip = '127.0.0.1'
bind_port = 8000


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print('Listening on {}:{}'.format(bind_ip, bind_port))

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
	global paddle1_move,barrier,p1_rt,paddle2_move,p2_rt
	client_socket.send(b'connectserver')
	while True:
		request = client_socket.recv(1024)
		print('Received {}'.format(request))
		msg = json.loads(request)

		if msg['type']=='info':
			print('info')
			if msg['who']=='P1':
				print('P1 info')
				paddle1_move=msg['content']
				p1_rt=time.time()
				barrier[0]=1
				if barrier[1]==1:
					# send_to_webserver()
					# game('on_p1')
					client_socket.send(b'ACK!')
					

			elif msg['who']=='P2':
				print('P2 info')
				paddle2_move=msg['content']
				p2_rt=time.time()
				barrier[1]=1
				print('barrier',barrier)
				if barrier[0]==1:
					# send_to_webserver()
					# game('on_p2')
					client_socket.send(b'ACK!')

		elif msg['type']=='connected':
			
			if msg['who']=='P1':
				print('P1 in')
			elif msg['who']=='P2':
				print('P2 in')

		elif msg['type']=='disconnect':
			if msg['who']=='P1':
				print('P1 leave')
			elif msg['who']=='P2':
				print('P2 leave')

		
		# client_socket.close()


while True:
	client_sock, address = server.accept()
	print('Accepted connection from {}:{}'.format(address[0], address[1]))
	client_handler = threading.Thread(
		target=handle_client_connection,
		args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
	)
	client_handler.start()