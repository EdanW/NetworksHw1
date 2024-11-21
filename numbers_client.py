#!/usr/bin/env python3

from socket import *
import sys


def recv_all_as_string(client_socket):
    msg = ''
    while msg[-1] != '\t':
        tmp = client_socket.recv(1024).decode('utf-8')
        # Handle FIN packet case
        if not tmp:
            client_socket.close()
            return ''
        msg += tmp
    return msg[:-1]


def validate_login_input(user, pw):
    return user[0:7] == "User: " and pw[0:11] == "Password: "


def start_client():
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

    welcome_msg = client_socket.recv(1024).decode('utf-8')
    if welcome_msg != 'Welcome! Please log in.':
        print('Did not receive proper welcoming message from server, shutting down connection')
        client_socket.close()
        exit(1)

    # Login loop
    successful_login = False
    while True:
        user_input = input()
        password_input = input()
        if not validate_login_input(user_input, password_input):
            print("Unexpected login format")
            client_socket.close()
            break
        user_input = user_input[7:]
        password_input = password_input[11:]
        login_msg = user_input + '\n' + password_input + '\t'
        client_socket.sendall(login_msg.encode('utf-8'))

        response = recv_all_as_string(client_socket).decode('utf-8')

        if response == "Failed to login.":
            print(response)
        else:
            if not response:
                # Handle FIN case
                break
            elif response == f"Hi {user_input}, good to see you":
                print(response)
                successful_login = True
            else:
                print(f"Internal error: unexpected server behavior. response was:{response}")
            break



    # Methods loops
    while successful_login:
        print('h')


if __name__ == "__main__":
    start_client()