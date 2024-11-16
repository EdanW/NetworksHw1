#!/usr/bin/env python3

from socket import *
import sys

def start_client():
    print('h')
    HOST_NAME = 'localhost'
    PORT = 1337

    # args validation
    if len(sys.argv) > 3:
        print('invalid number of arguments passed')
        exit(1)
    if len(sys.argv) >= 2:
        # todo validate a proper hostname (ip/name)
        HOST_NAME = sys.argv[1]
        if len(sys.argv) == 3:
            # todo validate a proper port number
            PORT = sys.argv[2]

    # Establish connection
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST_NAME, PORT))

    msg = client_socket.recv(1024).decode('utf-8')
    if msg != 'Welcome! Please log in.':
        print('Did not receive proper welcoming message from server')
        client_socket.close()
        exit(1)


    while True:
        msg = input() # input from cli/terminal
        msg += '$' # protocol
        client_socket.sendall(msg.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        # todo our own recv_all based on $ protocol
        if not response: # FIN
            client_socket.close()
            break

        print(response) # note- should our recv_all return bytes or string




if __name__ == "__main__":
    start_client()