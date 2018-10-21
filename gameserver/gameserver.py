import logging
from websocket_server import WebsocketServer
import subprocess
import time
import json,sys
global path
path="games/easy/codes/"

class MaxSizeList(object):

	def __init__(self, max_length):
		self.max_length = max_length
		self.ls = []

	def push(self, st):
		if len(self.ls) == self.max_length:
			return 1
		self.ls.append(st)
		return 0

	def pop_index(self,i):
		return self.ls.pop(i)

	def get_list(self):
		return self.ls

room_q=MaxSizeList(100)
server_q=MaxSizeList(50)
servs_full=0

def new_client(client, server):
	msg1="Hey all, a new client has joined us"
	server.send_message(client,msg1)

def message_received(client, server, message):
	#msg include code room logId language(compiler, Filename Extension)
	print("Client(%d) said: %s" % (client['id'], message))
	data = json.loads(message)
	print(data['room'])
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
	sandbox(language_res[0],path,filename)
	
	if room_q.push([data['room'],data['userId'],path,filename,data['player_list']]):
		print("full, need to wait(for a min)")
	else:
		print("add to room_q successfully")
					
	

	
def server_q_next(room,path_, filename):
	pass

def sandbox(compiler,path_, filename):
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	from subprocess import Popen, PIPE
	image='cce238a618539'
	try:
		p = Popen('sh script.sh '+image+' '+compiler+' '+path_+' '+filename+'',shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		print('stderr: ',stderr)
		print('stdout: ',stdout)
		# if p.stderr.readline():
		# 	print("error:")
		# 	line = p.stderr.readline()
		# 	while line:
		# 		print(line.strip())
		# 		line = p.stderr.readline()
		# else:
		# 	print("no error:")
		# 	line = p.stdout.readline()
		# 	while line:
		# 		print(line.strip())
		# 		line = p.stdout.readline()
	except Exception as e:
		print('e: ',e)
	

def save_code(code,log,room,user_id,language):
	# log=tuple([logId,gameId,p_cnt,game_p_cnt])
	logdata=json.loads(log)
	filename="%d_%s%s"%(logdata[0],user_id,language)
	f = open(path+filename, "w") 
	f.write(code)
	f.close()
	
	# logdata[2]+=1
	# if logdata[2]==logdata[3]:
	# 	execute_queue(logdata[0],room,logdata[4])
	return filename
	


def execute_queue(logId,room,user_id_list):
	roomname=room.split()
	
	if logId :
		#left first
		proc1 = subprocess.Popen(
			['python', '%s%d_%s.py'%(path,logId,user_id_list[0])],
			stdout=subprocess.PIPE)
		# proc2 = subprocess.Popen(
		# 	['python', '%s%d_%s.py'%(path,logId,user_id)],
		# 	stdout=subprocess.PIPE)	
		proc3 = subprocess.Popen(
			['python', '%spingpong.py'%path]+ roomname,
			stdout=subprocess.PIPE)
		out1, err1 = proc1.communicate()
		if(err1 is not None):
			print(err1.decode('utf-8'))
		# out2, err2 = proc2.communicate()
		# if(err2 is not None):
		# 	print(err2.decode('utf-8'))
		out3, err3 = proc3.communicate()
		if(err3 is not None):
			print(err3.decode('utf-8'))



server = WebsocketServer(6005, host='127.0.0.1')
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()