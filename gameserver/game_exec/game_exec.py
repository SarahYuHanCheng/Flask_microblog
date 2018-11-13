# game start and over msg both recv from gameserver.py 
# over: kill docker and send msg to notify gameserver

from websocket import create_connection
import json, sys,os
import subprocess

ws = create_connection("ws://localhost:6005")
serv_status=[0] * 5

def aws_container(log_id,userId,compiler,path_, filename):
	# 用 subprocess將欲執行的檔名當參數,執行 exec_script.sh, 使產生 docker container 來執行程式碼,指令如下 
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	from subprocess import Popen, PIPE
	try:
		userId = Popen(''+compiler+' '+path_+' '+filename+'',shell=True)
		return 0
	except Exception as e:
		print('e: ',e)
		return 1

def msg_handler(msg):
	# 每個 element的 內容：[data['log_id'],data['user_id'],\
	#	data['game_lib_id'],language_res[0],path,filename,data['player_list']]
	# 開 subprocess 
	for element in msg:
		code = (open(""+element[4]+element[5]))
		print(code)
		# 執行package
		merge_com_lib(code,element[4],element[5],element[3])
		aws_container(element[0],element[1],element[3],element[4],element[5])



def merge_com_lib(code,path,filename,compiler):
	# "w"上傳新的程式碼會直接取代掉
	# 加上不同語言與 webserver溝通的code
	try:
		os.makedirs( path )
	except:
		pass
	f = open("%s%s"%(path,filename), "w") 

	def set_lib(_compiler):
		language = {
			"gcc": ["c_com_lib.c"],
			"python3.7": ["py_com_lib.py"]
		}
		lib_file = compiler.get(_compiler, "Invalid month")
		return lib_file 
	com_lib_file = set_lib(compiler)

	with open(com_lib_file) as fin: 
		lines = fin.readlines() 
		for i, line in enumerate(lines):
			if i >= 0 and i < 6800:
				f.write(line)
		f.write(code)
		f.close()
		return 0
	f.write(code)
	f.close()
	return 0

# print("Sending 'Hello, World'...")
# ws.send(json.dumps({'from':"game_exec"}))
# recv_msg = ws.recv()
# msg_handler(recv_msg)
# merge_com_lib(recv_msg['code'], recv_msg['path'],recv_msg['filename'],recv_msg['compiler'])


import sched, time
s = sched.scheduler(time.time, time.sleep)
serv_status=[0] * 5
serv_status.append(1)
serv_status.insert(2,1)
serv_status.insert(5,1)
#[0, 0, 1, 0, 0, 1, 0, 1]
def get_serv_index(_lst):

	if len(_lst) > 0:
		index = _lst.pop(0)
		serv_status[index]= 1#log_id, serve for which log
		print('serv_index: ',index)

def check_serv_status():
	lst = [i for i,x in enumerate(serv_status) if x==0]
	get_serv_index(lst)
	s.enter(1, 1, check_serv_status)

s.enter(1, 1, check_serv_status)
# scheduler.enter(delay, priority, action, argument=(), kwargs={})
s.run()