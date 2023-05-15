import socket  
import json

class Client:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port

    def send_data(self, client, cmd, **kv):
        jd = {}
        jd['COMMAND'] = cmd
        jd['name'] = self.name
        jd['data'] = kv
        
        jsonstr = json.dumps(jd)
        print('send: ' + jsonstr)
        client.sendall(jsonstr.encode('utf8'))
    
    def run(self):
        client = socket.socket() 
        client.connect((self.host, int(self.port)))
        print(client.recv(1024).decode(encoding='utf8'))
        self.send_data(client, 'CONNECT')

        while True:
            msg=input("Enter the information you want to send:")
            self.send_data(client, 'SEND_DATA', data=msg)
        