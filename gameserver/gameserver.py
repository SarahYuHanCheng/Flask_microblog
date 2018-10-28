import logging
from websocket_server import WebsocketServer

import time
import json,sys
global path
path="games/easy/codes/"
game_exec_id=0
servs_full=0
servs_full_right=1


server = WebsocketServer(6005, host='127.0.0.1')
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()

def movetoserv_q(i,st):
	# 將room_q中第i個(到齊的)element移到 serv_q, 並執行 serv_q的第一個 element
	# 並比對i後面的 element是否為同一房間,是的話也同上一步驟
	
	room_list=room_q.get_list()
	serv_q.push(st,'s')
	for j in range(i,len(room_list)): #find the same room
		if room_list[i][0]==st[0]:
			serv_q.push(room_list[i],'s')
			room_list.pop(i)
			game_exec(serv_q.pop_first('s'))

def game_exec(st):
	# 接收 serv_q的 element, 用 ws傳給 exec主機
	# (game_exec_id 為 exec主機在 ws server上註冊的 client_id)
	# 將 element解開逐一放進json dict裡, 增加 code
	# {room_id, log_id, user_id, compiler, code, path, filename}
	global game_exec_id,server
	code = (open(""+st[2]+st[3]))
	print(code)
	packet=json.dumps({'room_id':st[0],'log_id':st[1],'user_id':st[2],'compiler':st[3],'code':code,'path':st[4],'filename':st[5]}
	# recv_msg['room'],recv_msg['userId'],recv_msg['compiler'],recv_msg['path'],recv_msg['filename']
	server.send_message(game_exec_id,packet)


class MaxSizeList(object):
	# room_q, serv_q皆使用此 list, push和 pop_first會依身份有不同的操作
	# push:同room會放一起,同時檢查是否到齊, 若到齊會將該room的第一個 element丟到 serv_q,(若 serv_q已滿,無法送出, 則將這些已到齊的 element移到room_q的第一位置)
	# pop_first: 1. game_exec呼叫serv_q的 pop 2. serv_q有空位, call room_q的pop
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
	# ws server的client 來源有2: 1. webserver 2. gamemain
	# 1. webserver: 先經過 sandbox, 將結果回傳給user, 確定要使用再排進 room_q
	# 2. gamemain: 某 room遊戲結束, 通知 game_exec kill 該 room的 dc container, 並執行< movetoserv_q >;
	# 續上：同時傳遞遊戲結果的訊息給 webserver (games/event.py 接收)

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
		if room_q.push([data['room'],logId,data['userId'],language_res[0],path,filename,data['player_list']],'r'):
			print("full, need to wait(for a min)")
		else:
			print("add to room_q successfully")
		
					

def sandbox(compiler,path_, filename):
	# 用 subprocess將預測試的檔名當參數執行 script.sh, 使產生 docker container 來驗證程式碼,指令如下 
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
	# 在呼叫 sandbox前 將程式碼依遊戲人數？分類？為路徑 存於 gameserver並回傳檔名
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
	





