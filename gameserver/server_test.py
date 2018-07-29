import logging
from websocket_server import WebsocketServer

def new_client(client, server):
    msg1="Hey all, a new client has joined us"
    server.send_message(client,msg1)

def message_received(client, server, message):
	# if len(message) > 200:
	# 	message = message[:200]+'..'
	print("Client(%d) said: %s" % (client['id'], message))

server = WebsocketServer(6005, host='127.0.0.1', loglevel=logging.INFO)
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()