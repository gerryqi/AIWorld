from server import Server
from client import Client
import threading

class Node:
    def __init__(self, client_name, self_host, self_port, send_host, send_port):
        self.client_name = client_name
        self.self_host = self_host
        self.self_port = self_port
        self.send_host = send_host
        self.send_port = send_port

    def run_server(self):
        server = Server(self.self_host, self.self_port)
        server.run()
    def run_client(self):
        client = Client(self.client_name, self.send_host, self.send_port)
        client.run()

    def run(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        client_thread = threading.Thread(target=self.run_client)
        client_thread.start()
