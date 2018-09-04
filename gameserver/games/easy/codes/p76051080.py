# -----------------------------------------
# Usercode - P1, the left one
# input: tuple([ball,paddle1,paddle2,cnt]) 
# 	ball_pos[x,y], paddle1_pos[y]
# output: paddle_vel[move_unit]
# -----------------------------------------
import time
from socketIO_client import SocketIO, LoggingNamespace

ball_pos=[[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=2
paddle_vel=0
count=0

def on_wait(msg):
	print("wait for other player")

def on_endgame(msg):
	print("end ball ",msg['msg'])
	raise SystemExit

def on_gameinfo(message):
	tuple_msg=message['msg']
	print(tuple_msg[0])
	cnt = tuple_msg[-1]
	print('cnt',cnt)
	if cnt>2:
		del ball_pos[0]
	ball_pos.append(tuple_msg[0])
	# print(ball_pos)
	
	run()
	communicate(cnt)


def run():
	global count
	count+=1
	if count>10:
		# time.sleep(1)
		count=0
	global paddle_vel
	if (ball_pos[-1][0]-ball_pos[-2][0]) <0: 
		print("ball moves left")
		if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
			print("ball moves down")
			paddle_vel=move_unit
		elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
			print("ball moves up")
			paddle_vel=-move_unit
	else: 
		paddle_vel=0
		print("ball moves right, no need to move paddle1")
	# ball_pos.pop()
	# paddle1_pos.pop()

def communicate(cnt):
	global paddle_vel
	socketIO.emit('P1',{'paddle_vel':paddle_vel,'cnt':cnt})

def score():# CPU, MEM Utility
	pass

socketIO=SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on('endgame',on_endgame)
socketIO.on('wait',on_wait)
socketIO.on('gameinfo',on_gameinfo)

socketIO.emit('P1_in')
socketIO.wait()