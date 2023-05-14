import argparse
import socket
import threading
from threading import Thread
import time
import json

# 定义默认参数
DEFAULT_LEADER_ID = 0
DEFAULT_LEADER_ADDRESS = 'localhost'
DEFAULT_LEADER_PORT = 8001
DEFAULT_HEARTBEAT_INTERVAL = 5
DEFAULT_TIMEOUT = 3
NODES = set()

server_socket = None  # 负责监听的socket
g_conn_pool = {}  # 连接池

def get_server_list(leader_host='localhost',leader_port=8001)->list:
    # 创建套接字对象并连接到服务器
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((leader_host,leader_port))
    # 发送请求消息到服务器
    request_message = 'GET_SERVER_LIST'
    client_socket.send(request_message.encode())
    # 获取服务器响应
    response_message = client_socket.recv(1024).decode()      
    # 关闭套接字连接
    client_socket.close()       
    return response_message

class Node:
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.nodes = NODES
        self.leader_id = DEFAULT_LEADER_ID
        self.leader_host = DEFAULT_LEADER_ADDRESS
        self.leader_port = DEFAULT_LEADER_PORT
        self.election_timeout = None
        self.heartbeat_interval = DEFAULT_HEARTBEAT_INTERVAL
        self.last_heartbeat_time = time.time() 
    
    def run(self):
        # 启动两个线程：一个负责作为Server监听其它节点发送的消息；
        # 另一个负责作为Client定时向Leader发送心跳消息。
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        # data = get_server_list()
        # # 解析响应消息
        # server_list = [server.split(':') for server in data.split(',')] 
        # for server in server_list:
        #     print(f"Connect to Server Host: {server[0]}, Port: {server[1]}")
        #     host = server[0]
        #     port = int(server[1])
        client_thread = threading.Thread(target=self.run_client)
        client_thread.start()

    def register_node(self):
        self.nodes.add(Node(self.id, self.host, self.port))
        print(f"The Node {node.id} is already registered with the cluster.")

    def remove_client(client_type):
        client = g_conn_pool[client_type]
        if None != client:
            client.close()
            g_conn_pool.pop(client_type)
            print("client offline: " + client_type)

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
                client_type = jd['client_type']
                if 'CONNECT' == cmd:
                    g_conn_pool[client_type] = client
                    print('on client connect: ' + client_type, info)
                elif 'SEND_DATA' == cmd:
                    print('recv client msg: ' + client_type, jd['data'])
            except Exception as e:
                print(e)
                self.remove_client(client_type)
                break

    def accept_client(self,server_socket):
        """
        接收新连接
        """
        while True:
            client, info = server_socket.accept()  # 阻塞，等待客户端连接
            # 给每个客户端创建一个独立的线程进行管理
            thread = Thread(target=self.message_handle, args=(client, info))
            # 设置成守护线程
            thread.setDaemon(True)
            thread.start()

    def run_server(self):
        # 创建套接字对象
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 将套接字绑定到本地主机和端口号上
        server_socket.bind((self.host, self.port))
        # 开始监听传入连接
        server_socket.listen()
        # 注册Server到集群
        self.register_node()

        # 等待传入连接请求并接受它们
        self.accept_client(server_socket)

    def run_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接到远程主机
        client_socket.connect((self.host, self.port))
        while True:
            # 发送消息
            message = input('Client:Enter message to send: ').encode()
            if message == b'exit':
                break
            client_socket.sendall(message)
            # 接收来自服务器的响应
            data = client_socket.recv(1024)
            # 处理响应数据并输出
            print('Client Received:', data.decode())
        # 关闭连接
        client_socket.close()
             
# python __main__.py --id 0 --host "localhost" --port 8001  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P2P Network Node')
    parser.add_argument("--id", type=int,help="node id", required=True)
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Bind address')
    parser.add_argument('--port', type=int, required=True, help='Listen port')
    args = parser.parse_args()
    node = Node(args.id, args.host, int(args.port))
    node.run()
    