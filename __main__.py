import argparse
import socket
import threading
import time

# 定义默认参数
DEFAULT_LEADER_ID = 0
DEFAULT_LEADER_ADDRESS = 'localhost'
DEFAULT_LEADER_PORT = 8000
DEFAULT_HEARTBEAT_INTERVAL = 5
DEFAULT_TIMEOUT = 3
NODES = set()

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
        client_thread = threading.Thread(target=self.run_client)
        client_thread.start()

    def register_node(self):
        self.nodes.add(Node(self.id, self.host, self.port))
        print(f"The Node {node.id} is already registered with the cluster.")

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
        conn, address = server_socket.accept()
        while True:
            # 处理传入的数据，并回复一个响应
            data = conn.recv(1024)
            # 处理响应数据并输出
            print('Server Received:', data.decode())
            message = input('Server:Enter message to send: ').encode()
            if message == b'exit':
                break
            conn.sendall(message)        
        # 关闭连接
        conn.close()
        server_socket.close()

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
    node = Node(args.id, args.host, args.port)
    node.run()
    