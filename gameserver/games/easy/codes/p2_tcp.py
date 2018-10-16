import socket , time, json
  
address = ('127.0.0.1', 8800)  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s.connect(address)  
msg={'type':'connect','who':'P2','content':'in'}	
str_ = json.dumps(msg)
# binary = ' '.join(format(ord(letter), 'b') for letter in str_) 
binary =str_.encode()
s.send(binary) 
time.sleep(5)
  
cnt =3000
while cnt>0:
	data = s.recv(2048)  
	print(data)
	msg={'type':'info','who':'P2','content':3}
	
	str_ = json.dumps(msg)# binary = ' '.join(format(ord(letter), 'b') for letter in str_) 
	binary =str_.encode()
	s.send(binary) 
	cnt-=1
	time.sleep(0.005)
  
s.close()  