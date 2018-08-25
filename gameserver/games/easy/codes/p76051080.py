# -----------------------------------------
# Usercode - P1, the left one
# input: tuple([ball,paddle1,paddle2]) 
# 	ball_pos[x,y], paddle1_pos[y]
# output: paddle_vel[move_unit]
# -----------------------------------------
import time
from socketIO_client import SocketIO, LoggingNamespace
ball_pos=[[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=5
paddle_vel=0


def on_wait(msg):
	print("wait for other player")
def on_endgame(msg):
	print("end ball ",msg['msg'])
	raise SystemExit

def on_gameinfo(message):
	tuple_msg=message['msg']
	print(tuple_msg[0])
	ball_pos.append(tuple_msg[0])
	paddle1_pos.append(tuple_msg[1])
	
	run()
	communicate()


def run():
	global paddle_vel
	if (ball_pos[-1][0]-ball_pos[-2][0]) <0: 
		print("ball moves left")
		if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
			# print("ball moves down")
			paddle_vel=move_unit
		elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
			# print("ball moves up")
			paddle_vel=-move_unit
	else: 
		print("ball moves right, no need to move paddle1")

def communicate():
	global paddle_vel
	time.sleep(0.01)
	socketIO.emit('P1',paddle_vel)

def score():# CPU, MEM Utility
	pass

socketIO=SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on('wait',on_wait)
socketIO.on('gameinfo',on_gameinfo)
socketIO.on('endgame',on_endgame)
socketIO.emit('P1_in')
socketIO.wait(seconds=60)