#!/usr/bin/env python3

from socket import *
import select
import sys


def print_login_message(client_socket):
    message = 'Welcome! Please log in'
    client_socket.send(message.encode())

def command_handler(conn_socket, message):
    command = message.split(' ')[0]
    print(message, command)
    if command == 'max:':
        print('max')
    elif command == 'calculate:':
        print('calc')
    elif command == 'factors:':
        print('factors')
    elif command == 'quit':
        if message != 'quit':
            send_invalid_input_error(conn_socket)
        disconnect_socket(conn_socket)

def send_invalid_input_error(conn_socket):
    print(conn_socket)
    # todo write this func (send to conn_socket the message via send_all?)

def recv_all(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        return data
    # Note: I hope this works as expected.

def disconnect_socket(conn_socket):
    sockets_list.remove(conn_socket)
    del clients[conn_socket]
    conn_socket.close()

def process_file(file_name, users_dic):
    try:
        with open(file_name, 'r') as text_file:
            lines = text_file.readlines()
        for line in lines:
            user = line.strip().split("\t")
            users_dic[user[0]] = user[1]
    except:
        print('error in processing file')
        exit(1)

# Global vars
sockets_list = []
clients = {}  # Dictionary to keep track of client addresses

def start_server():
    # Server Configuration
    HOST = '127.0.0.1'  # Localhost
    PORT = 1337
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print('invalid number of arguments passed')
        exit(1)
    if len(sys.argv) == 2:
        PORT = sys.argv[2]
    file_path = sys.argv[1]
    #loads all the users information to a dictionary
    known_users_dict = {}
    process_file(file_path,known_users_dict)

    logged_in_users_sockets_list = []

    #creats new socket
    server_socket = socket(family=AF_INET, type=SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    # Step 5: Use lists to keep track of sockets
    sockets_list.append(server_socket) # List of all connected sockets

    # Step 6: Main loop to handle multiple clients
    while True:
        # Step 7: Use `select` to wait for socket events
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        # Step 8: Iterate over readable sockets
        for active_socket in read_sockets:
            # Step 9: If it's the server socket, accept a new connection
            if active_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                print_login_message(client_socket)

            # Step 10: Otherwise, it's an existing client socket with data
            else:
                message = recv_all(active_socket)  # Receive full message
                decoded_message = message.decode("utf-8")

                # Step 10.5 if youre not logged in, do so. if you dont i kick u
                if active_socket not in logged_in_users_sockets_list:
                    print('placeholder')
                    is_valid_user = False;
                    #todo find out how to validate logging in
                    if is_valid_user:
                        logged_in_users_sockets_list.append(active_socket)
                    else:
                        disconnect_socket(active_socket)
                        continue

                # Step 12: If no data is received, the client has disconnected
                if not decoded_message:
                    disconnect_socket(active_socket)
                    continue

                # Step 13: If data is received, USE HANDLER
                else:
                    command_handler(active_socket, decoded_message)


        # Step 14: Handle any exceptional conditions on sockets
        for active_socket in exception_sockets:
            disconnect_socket(active_socket)


# comment :)

if __name__ == "__main__":
    start_server()
