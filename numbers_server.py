#!/usr/bin/env python3
import math
import socket
from socket import *
import select
import sys


def print_login_message(client_socket):
    message = 'Welcome! Please log in$'
    client_socket.send(message.encode())

def command_handler(conn_socket, message):
    data = message.split(':')[0]
    command = data[0]
    expression = data[1]
    print(message, command)
    if command == 'max:':
        print('max')
        return maximum(expression)
    elif command == 'calculate:':
        print('calc')
        return  calculate(expression)
    elif command == 'factors:':
        print('factors')
        return get_prime_factors(expression)
    elif command == 'quit':
        return 'quit'

def send_invalid_input_error(conn_socket):
    print(conn_socket)
    # todo write this func (send to conn_socket the message via send_all?)

def disconnect_socket(conn_socket):
    sockets_list.remove(conn_socket)
    del clients[conn_socket]
    conn_socket.close()

def calculate(expression):
    """
    @pre: the form of expression is "X "operation" Y"
    @pre: if the math operation is "/", Y!=0
    """
    expr_arr = expression.split()
    #converts the numbers from string to int
    expr_arr[0] = int(expr_arr[0])
    expr_arr[2] = int(expr_arr[2])

    if expression[1] == "+":
            return  str(expr_arr[0] + expr_arr[2])
    elif expression[1] == "-":
            return str(expr_arr[0] - expr_arr[2])
    elif expression[1] == "*":
            return  str(expr_arr[0] * expr_arr[2])
    elif  expression[1] == "/":
            return  str(expr_arr[0] / expr_arr[2])
    elif expression[1] == "^":
            return str(math.pow(expr_arr[0],expr_arr[2]))


def maximum(numbers):
    numbers_arr = [int(x) for x in numbers.split(" ")]
    return str(max(numbers_arr))


def is_prime(n):
    """Checks if a number is prime"""
    if n == 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    #Checks if there is a number up to the range of the root of n that divides n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False

    return True


def get_prime_factors(n):
    """
    returns a set of all the prime factors of n
    """
    factors = set()

    while n % 2 == 0:
        factors.add(2)
        n //= 2

    for i in range(3, int(n ** 0.5) + 1, 2):
        while n % i == 0:
            if is_prime(i):
                factors.add(i)
            n //= i

    return str(factors)


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

def proccess_login_data(login_info):
    """
    read login info and return a tuple of username and password
    """
    #todo decide in which format the client send us the information so we'll
    # know how to break and use it
    return None


# Global vars
sockets_list = []
clients = {}  # Dictionary to keep track of client addresses
clients_messages = {}

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
    with  socket.socket(family=AF_INET, type=SOCK_STREAM) as server_socket:
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
                    #gets the address of the active socket for dictionary searches
                    client_address = clients[active_socket]

                    if client_address not in clients_messages:
                        clients_messages[client_address]=""
                    clients_messages[client_address] += active_socket.recv(1024)

                    message_builder = clients_messages[client_address].decode("utf-8")

                    #check if we got the full message
                    if message_builder[-1] == "$":
                        # Step 10.5 if you're not logged in, do so. if you don't i kick u
                        if active_socket not in logged_in_users_sockets_list:

                            username, password = proccess_login_data(message_builder)

                            if username in known_users_dict and known_users_dict[username] == password:
                                logged_in_users_sockets_list.append(active_socket)
                            else:
                                #the user can try again so no need to close the socket
                                active_socket.send("Failed to login.$".encode("utf-8"))
                            continue

                        # Step 13: you're logged in, so you probably sent us some command
                        else:
                            #handle this case first because it requires removing stuff from data structures
                            if message_builder == 'quit$':
                                send_invalid_input_error(active_socket)
                                clients_messages.pop(client_address)
                                logged_in_users_sockets_list.remove(active_socket)
                                clients.pop(active_socket)
                                disconnect_socket(active_socket)

                            message_to_send = command_handler(active_socket, message_builder)+'$'
                            active_socket.send(message_to_send.encode("utf-8"))

                        #ready for new command
                        clients_messages[client_address] = ""



                        # Step 14: Handle any exceptional conditions on sockets
            for active_socket in exception_sockets:
                disconnect_socket(active_socket)




if __name__ == "__main__":
    start_server()
