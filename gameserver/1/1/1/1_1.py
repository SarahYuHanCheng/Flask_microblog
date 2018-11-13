#!/usr/bin/python
import socket , time, json,sys
  
address = ('127.0.0.1', 8800)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
  
s_sucess=""
s_sucess=s.connect(address)

# while s_sucess is not None:
# 	try:
# 		s_sucess=s.connect(address)
# 	except Exception as e:
# 		print(e) 
# 		continue
# 	finally:
# 		time.sleep(1)
	 
def game_over():
	# time.sleep(8)
	pass
	# sys.exit()

print(s_sucess)
connecttoserver = s.recv(2048)
msg={'type':'connect','who':'P1','content':'in'}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


ball_pos=[[0,0],[0,0],[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3
paddle_vel=0

def on_gameinfo(message):
	print(type(message))
	global paddle_vel
	# tuple_msg=message['content']
	# # tuple([ball,paddle1[1],paddle2[1],cnt])
	# cnt = tuple_msg[-1]
	# if cnt>2:
	# 	del ball_pos[0]
	# ball_pos.append(tuple_msg[0])

	run()
	communicate('info',paddle_vel)


def run():
	global paddle_vel,ball_pos,move_unit
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

def communicate(type_class,content):
	global paddle_vel,s
	msg={'type':type_class,'who':'P1','content':content, 'cnt':cnt}
	
	str_ = json.dumps(msg)
	binary =str_.encode()
	s.send(binary) 

def score():# CPU, MEM Utility
	communicate('score',['cpu','mem'])
	gameover()
  


cnt =6000
while cnt>0:
	data = s.recv(2048)
	if data==b"":
		continue
	else:
		msg_recv = json.loads(data)
		# 判斷 msg 類型, gameinfo or gameover
		# msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],cnt])}
		# msg={'type':'over','content':"www"}
		print(msg_recv)
		if msg_recv['type']=='info':
			on_gameinfo(msg_recv)
		else if msg_recv['type']=='over':
			score()
		else:
			pass
	cnt-=1
	time.sleep(0.03)

msg_leave={'type':'disconnect','who':'P1','content':'0'}	
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
