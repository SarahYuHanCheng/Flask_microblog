import logging
from websocket_server import WebsocketServer
import subprocess
import time
import json

def new_client(client, server):
    msg1="Hey all, a new client has joined us"
    server.send_message(client,msg1)

def message_received(client, server, message):

	print("Client(%d) said: %s" % (client['id'], message))
	data = json.loads(message)
	print(data['room'])
	save_code(data['code'],data['logId'],data['room'])
	#取出msg中的logId當作檔名存成.py檔, 放進queue
def save_code(code,logId,room):
	f = open("games/easy/codes/%d.py"%logId, "w") 
	f.write(code)#上傳新的程式碼會直接取代掉
	f.close()

def execute_queue():
	#在call subprocess 來執行 logId.py
	if message :
		proc1 = subprocess.Popen(
			['afplay', '1.wav'],
			stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(
			['afplay', '3.wav'],
			stdout=subprocess.PIPE)

		try:
			out1, err1 = proc1.communicate(timeout=2)
			out2, err2 = proc2.communicate(timeout=2)
		except subprocess.TimeoutExpired:
			proc1.terminate()
			proc1.wait()
			proc2.terminate()
			proc2.wait()		




server = WebsocketServer(6005, host='127.0.0.1', loglevel=logging.INFO)
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()