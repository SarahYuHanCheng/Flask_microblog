import socket , time, json
  
address = ('127.0.0.1', 8000)  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s.connect(address) 

msg={'type':'connect','who':'P1','content':'in'}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary) 

  
cnt =100
while cnt>0:
	data = s.recv(2048)  
	print(data)
	msg={'type':'info','who':'P1','content':cnt}
	
	str_ = json.dumps(msg)
	binary =str_.encode()
	s.send(binary) 
	cnt-=1
	time.sleep(0.001)

msg={'type':'disconnect','who':'P1','content':cnt}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary) 
s.close()  