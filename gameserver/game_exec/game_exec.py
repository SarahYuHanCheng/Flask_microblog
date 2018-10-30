# game start and over msg both recv from gameserver.py 
# over: kill docker and send msg to notify gameserver

from websocket import create_connection
import json, sys,os
import subprocess

ws = create_connection("ws://localhost:6005")
recv_msg=[]
# def aws_container(room_name,userId,compiler,path_, filename):
# 	# 用 subprocess將欲執行的檔名當參數,執行 exec_script.sh, 使產生 docker container 來執行程式碼,指令如下 
# 	# sh test.sh cce238a618539(imageID) python3.7 output.py 
# 	from subprocess import Popen, PIPE
# 	image='cce238a618539'
# 	try:
# 		# room_name,userId,path,filename,'player_list'
# 		p = Popen('sh exec_script.sh '+image+' '+compiler+' '+path_+' '+filename+'',shell=True, stdout=PIPE, stderr=PIPE)
# 		stdout, stderr = p.communicate()
# 		print('stdout: ',stdout)
# 		return 0
# 	except Exception as e:
# 		print('e: ',e)
# 		return 1

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

print("Sending 'Hello, World'...")
ws.send(json.dumps({'from':"game_exec"}))
recv_msg = ws.recv()
merge_com_lib(recv_msg['code'], recv_msg['path'],recv_msg['filename'],recv_msg['compiler'])
# aws_container(recv_msg['room_name'],recv_msg['userId'],recv_msg['game_id'],recv_msg['compiler'],recv_msg['code'])

print("Received '%s'" % recv_msg)

