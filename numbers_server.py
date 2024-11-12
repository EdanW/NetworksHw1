#!/usr/bin/env python3

from socket import *
import select
import sys



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


def start_server():
    # Server Configuration
    HOST = '127.0.0.1'  # Localhost
    PORT = 1337
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print('invalid number of arguments passed')
        exit(1)
    if len(sys.argv) == 2:
        PORT = sys.argv[2]
    file_name = sys.argv[1]
    #loads all the users information to a dictionary
    known_users_dict = {}
    process_file(file_name,known_users_dict)

    logged_in_users_sockets_list = []

    #creats new socket
    server_socket = socket(family=AF_INET, type=SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    # Step 5: Use lists to keep track of sockets
    sockets_list = [server_socket]  # List of all connected sockets
    clients = {}  # Dictionary to keep track of client addresses

    # Step 6: Main loop to handle multiple clients
    while True:
        # Step 7: Use `select` to wait for socket events
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        # Step 8: Iterate over readable sockets
        for notified_socket in read_sockets:
            # Step 9: If it's the server socket, accept a new connection
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                print_login_message(client_socket)

            # Step 10: Otherwise, it's an existing client socket with data
            else:

                message = notified_socket.recv(1024)  # Receive up to 1024 byte
                decoded_message = message.decode("utf-8")
                # todo understand how to receive entire message even if its every long

                # Step 10.5 if youre not logged in, do so. if you dont i kick u
                if client_socket not in logged_in_users_sockets_list:
                    print('placeholder')
                    #todo find out how to validate logging in
                # Step 11: Receive data from the client

                # Step 12: If no data is received, the client has disconnected
                if not message:
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()  # Closes the connection properly
                    continue

                # Step 13: If data is received, USE HANDLER


        # Step 14: Handle any exceptional conditions on sockets
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


def print_login_message(client_socket):
    message = 'Welcome! Please log in'
    client_socket.send(message.encode())

def command_handler():
    print('placeholder')


if __name__ == "__main__":
    start_server()
