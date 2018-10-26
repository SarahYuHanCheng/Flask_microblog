import logging
from websocket_server import WebsocketServer

import time
import json,sys
global path
path="games/easy/codes/"
game_exec_id=0
servs_full=0
servs_full_right=1

def movetoserv_q(i,st):
	
	room_list=room_q.get_list()
	serv_q.push(st,'s')
	for j in range(i,len(room_list)): #find the same room
		if room_list[i][0]==st[0]:
			serv_q.push(room_list[i],'s')
			room_list.pop(i)
	servers_exec(serv_q.pop_first('s'))

def servers_exec(st):
	global game_exec_id
	# st=[data['room'],data['userId'],path,filename,data['player_list']]
	# logId?, room, user_id_list
	code = (open(""+st[2]+st[3]))
	print(code)
	json.dumps({'room_id':st[0],'player_id':st[1],'code':editor_content,'logId':st[2],'language':"python",}
	server.send_message(game_exec_id,st)


class MaxSizeList(object):
	
	def __init__(self, max_length):
		self.max_length = max_length
		self.ls = []

	def push(self, st,qclass):
		global servs_full,servs_full_right
		if len(self.ls) == self.max_length:
			if qclass=='s':
				while not servs_full_right:
					pass
				servs_full_right=0 # lock for others
				servs_full=1
			return 1
		if qclass=='s':
			servs=self.ls
			servs.append(st)
			return 0
		else:
		# find same room, pop playerlist, 
			rooms=self.ls
			if len(rooms)==0:
				rooms.append(st)
				return 0
			for i in range(0,len(rooms)):#R2
				if st[0]==rooms[i][0]: #find same room
					(rooms[i][3]).remove(st[1])
					st[3]=rooms[i][3]
					while not servs_full_right:
						pass
					servs_full_right=0
					if not servs_full:
						if len(rooms[i][3])==0: #all arrived
							movetoserv_q(i,st)
						return 0
					else:
						rooms.insert(i+1,st)#add new upload to room
						pass # not add to serv active, wait for serv notify
					return 0
			rooms.append(st)
			return 0

	def pop_first(self,qclass):
		global servs_full, servs_full_right
		while not servs_full_right:
			pass
		servs_full_right=0
		if qclass=='s' and servs_full:
			servs_full_right=0
			s_pop=self.ls.pop(0) # need pop first, cause push to it later
			rs=room_q.get_list()
			for i in range(0,len(rs)):#find the all arrived room
				if len(rs[i][3])==0:
					movetoserv_q(i,rs[i])
					return s_pop
			servs_full=0
			servs_full_right=1
			return s_pop
		return self.ls.pop(0) #qclass==r
	def get_list(self):
		return self.ls
	

room_q=MaxSizeList(100)
serv_q=MaxSizeList(50)

def new_client(client, server):
	msg1="Hey all, a new client has joined us"
	# server.send_message(client,msg1)


def message_received(client, server, message):
	#msg include code room logId language(compiler, Filename Extension)
	print("Client(%d) said: %s" % (client['id'], message))
	global game_exec_id
	data = json.loads(message)
	if data['from']=='servers':
		game_exec_id =client['id']
	elif data['from']=='game':
		print("game")
	logId=1
	gameId=1
	p_cnt=0#data['logId']
	game_p_cnt=1
	user_id_list=[data['userId']]#left,right
	log=tuple([logId,gameId,p_cnt,game_p_cnt,user_id_list])
	def set_language(language):
		compiler = {
			"c": ["gcc",".c"],
			"python": ["python3.7",".py"],
			"shell": ["sh",".sh"]
		}
		language_obj = compiler.get(language, "Invalid month")
		return language_obj 
	language_res = set_language(data['language'])
	filename=save_code(data['code'],json.dumps(log),data['room'],data['userId'],language_res[1])
	# path 
	# filename include .xxx
	if sandbox(language_res[0],path,filename):
		if room_q.push([data['room'],data['userId'],logId,path,filename,data['player_list']],'r'):
			print("full, need to wait(for a min)")
		else:
			print("add to room_q successfully")
		
					

def sandbox(compiler,path_, filename):
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	from subprocess import Popen, PIPE
	image='cce238a618539'
	try:
		p = Popen('sh script.sh '+image+' '+compiler+' '+path_+' '+filename+'',shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		print('stderr: ',stderr)
		print('stdout: ',stdout)
		return 0
	except Exception as e:
		print('e: ',e)
		return 1
	

def save_code(code,log,room,user_id,language):
	# log=tuple([logId,gameId,p_cnt,game_p_cnt])
	logdata=json.loads(log)
	filename="%d_%s%s"%(logdata[0],user_id,language)#logId,userId
	f = open(path+filename, "w") 
	f.write(code)
	f.close()
	
	# logdata[2]+=1
	# if logdata[2]==logdata[3]:
	# 	execute_queue(logdata[0],room,logdata[4])
	return filename
	





server = WebsocketServer(6005, host='127.0.0.1')
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()