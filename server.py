import socket  # 导入 socket 模块
from threading import Thread
import time
import json

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.g_conn_pool = {}
        self.g_socket_server = None
        self.init()

    def init(self):
        """
        初始化服务端
        """
        global g_socket_server
        g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        g_socket_server.bind((self.host, int(self.port)))
        g_socket_server.listen(50)  # 最大等待数（有很多人理解为最大连接数，其实是错误的）
        print("server start，wait for client connecting...")

    def accept_client(self):
        """
        接收新连接
        """
        while True:
            client, info = g_socket_server.accept()  # 阻塞，等待客户端连接
            # 给每个客户端创建一个独立的线程进行管理
            thread = Thread(target=self.message_handle, args=(client, info))
            # 设置成守护线程
            thread.daemon = True
            thread.start()
    
    
    def message_handle(self,client, info):
        """
        消息处理
        """
        client.sendall("connect server successfully!".encode(encoding='utf8'))
        while True:
            try:
                bytes = client.recv(1024)
                msg = bytes.decode(encoding='utf8')
                jd = json.loads(msg)
                cmd = jd['COMMAND']
                name = jd['name']
                if 'CONNECT' == cmd:
                    self.g_conn_pool[name] = client
                    print('on client connect: ' + name, info)
                elif 'SEND_DATA' == cmd:
                    print('recv client msg: ' + name, jd['data'])
            except Exception as e:
                print(e)
                self.remove_client(name)
                break

    def remove_client(self, name):
        client = self.g_conn_pool[name]
        if None != client:
            client.close()
            self.g_conn_pool.pop(name)
            print("client offline: " + name)
    def run(self):
        # 新开一个线程，用于接收新连接
        thread = Thread(target=self.accept_client)
        thread.daemon = True
        thread.start()
        # 主线程逻辑
        while True:
            time.sleep(0.1)