import socket , time, json
  
address = ('127.0.0.1', 8800)  # 140.116.82.229
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s.connect(address) 

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
	# tuple_msg=message['content']
	# print(tuple_msg[0])
	# cnt = tuple_msg[-1]
	# print('cnt',cnt)
	# if cnt>2:
	# 	del ball_pos[0]
	# ball_pos.append(tuple_msg[0])
	# print(ball_pos)
	
	run()
	communicate(cnt)


def run():
	# global count
	# count+=1
	# if count>10:
	# 	time.sleep(3)
		# count=0
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
	# ball_pos.pop()
	# paddle1_pos.pop()

def communicate(cnt):
	global paddle_vel,s
	msg={'type':'info','who':'P1','content':paddle_vel, 'cnt':cnt}
	
	str_ = json.dumps(msg)
	binary =str_.encode()
	s.send(binary) 

def score():# CPU, MEM Utility
	pass
  
cnt =2500
while cnt>0:
	data = s.recv(2048) 
	# print('%s, %d'%(data,cnt))
	msg_decode = data.decode('UTF8')
	print('Received {}'.format(msg_decode))
	# msg = json.loads(msg_decode)
	on_gameinfo(data)
	
	cnt-=1
	time.sleep(0.001)

msg={'type':'disconnect','who':'P1','content':0}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary) 
s.close()  