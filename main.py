import argparse
from node import Node

# python main.py --client_name "Node0" --self_host "localhost" --self_port 8712 --send_host "localhost" --send_port 8712
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P2P Network Server')
    parser.add_argument('--client_name', type=str, help='Node Name')
    parser.add_argument('--self_host', type=str, default='127.0.0.1', help='Bind address')
    parser.add_argument('--self_port', type=int, required=True, help='Listen port')
    parser.add_argument('--send_host', type=str, default='127.0.0.1', help='Send address')
    parser.add_argument('--send_port', type=int, required=True, help='Send port')
    args = parser.parse_args()
    
    node = Node(args.client_name, args.self_host, args.self_port,args.send_host,args.send_port)
    node.run()
