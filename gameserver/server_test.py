import socket, base64, hashlib
if __name__ == "__main__":
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ("127.0.0.1", 6005)
    serverSocket.bind(host)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.listen(5)
    print("server running")
    while True:
        print("getting connection")
        clientSocket, addressInfo = serverSocket.accept()
        print("get connected")
        receivedData = str(clientSocket.recv(2048))
        print(receivedData)
        entities = receivedData.split("\\r\\n")

        Sec_WebSocket_Key = entities[5].split(":")[1].strip() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        print("key ", Sec_WebSocket_Key)
        response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
        response_key_str = str(response_key)
        response_key_str = response_key_str[2:30]
        # print(response_key_str)
        response_key_entity = "Sec-WebSocket-Accept: " + response_key_str +"\r\n"
        clientSocket.send(bytes("HTTP/1.1 101 Web Socket Protocol Handshake\r\n", encoding="utf8"))
        clientSocket.send(bytes("Upgrade: websocket\r\n", encoding="utf8"))
        clientSocket.send(bytes(response_key_entity, encoding="utf8"))
        clientSocket.send(bytes("Connection: Upgrade\r\n\r\n", encoding="utf8"))
        print("send the hand shake data")