import logging
from websocket_server import WebsocketServer
import subprocess
import time
import json,sys
global path
path="games/easy/codes/"
def new_client(client, server):
    msg1="Hey all, a new client has joined us"
    server.send_message(client,msg1)

def message_received(client, server, message):
	#msg include code room logId
	print("Client(%d) said: %s" % (client['id'], message))
	data = json.loads(message)
	print(data['room'])
	logId=1
	gameId=1
	p_cnt=0#data['logId']
	game_p_cnt=1
	user_id_list=['P76051080','PpP']#left,right
	log=tuple([logId,gameId,p_cnt,game_p_cnt,user_id_list])
	save_code(data['code'],json.dumps(log),data['room'],data['userId'])
	
def save_code(code,log,room,user_id):
	# log=tuple([logId,gameId,p_cnt,game_p_cnt])
	logdata=json.loads(log)
	f = open("%s%d_%s.py"%(path,logdata[0],user_id), "w") 
	f.write(code)
	f.close()
	
	logdata[2]+=1
	if logdata[2]==logdata[3]:
		execute_queue(logdata[0],room,logdata[4])
	


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
