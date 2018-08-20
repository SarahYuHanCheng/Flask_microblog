# -----------------------------------------
# Usercode - P1, the left one
# input: tuple([ball,paddle1,paddle1]) 
# 	ball_pos[x,y], paddle1_pos[y]
# output: paddle[y]
# -----------------------------------------
import time
from socketIO_client import SocketIO, LoggingNamespace
ball_pos=[[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3


def on_gameinfo(message):
	print("on_gameinfo")
	tuple_msg=message['msg']
	ball_pos.append(tuple_msg[0])
	print(ball_pos)
	run()
	communicate()


def run():
	if (ball_pos[-1][0]-ball_pos[-2][0]) <0: 
		print("ball moves left")
		if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
			print("ball moves down")
			paddle1_pos.append(paddle1_pos[-1]+move_unit)

		elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
			print("ball moves up")
			paddle1_pos.append(paddle1_pos[-1]-move_unit)
	else: 
		print("ball moves right, no need to move paddle2")

def communicate():
	time.sleep(0.1)
	socketIO.emit('P1',paddle1_pos[-1])

def score():# CPU, MEM Utility
	pass

socketIO=SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on('gameinfo',on_gameinfo)
socketIO.emit('P1',paddle1_pos[-1])
socketIO.wait(seconds=8)