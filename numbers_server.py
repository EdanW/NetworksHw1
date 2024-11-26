#!/usr/bin/env python3
import math
import socket
from socket import *
import select
import sys


def print_login_message(client_socket):
    message = 'Welcome! Please log in.\t'
    client_socket.send(message.encode())


def command_handler(message):
    data = message[:-1].split(':')
    command = data[0]
    expression = data[1]
    if command == 'm':
        return maximum(expression)
    elif command == 'c':
        return  calculate(expression)
    elif command == 'f':
        return get_prime_factors(expression)
    else:
        return "error: command not found"



def disconnect_socket(conn_socket):
    sockets_list.remove(conn_socket)
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
    result = 0
    if expr_arr[1] == "+":
            result = expr_arr[0] + expr_arr[2]
    elif expr_arr[1] == "-":
            result = expr_arr[0] - expr_arr[2]
    elif expr_arr[1] == "*":
            result = expr_arr[0] * expr_arr[2]
    elif  expr_arr[1] == "/":
            result = round(expr_arr[0] / expr_arr[2], 2)
    elif expr_arr[1] == "^":
            try:
                result = math.pow(expr_arr[0],expr_arr[2])
            except ValueError:
                return "error: result is too big"
    return str(result) if (INT32_MAX >= result >= INT32_MIN) else "error: result is too big"


def maximum(numbers):
    numbers = numbers.replace('(', '').replace(')', '')
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
    n = int(n.strip())
    factors = set()

    while n % 2 == 0:
        factors.add(2)
        n //= 2

    for i in range(3, int(n ** 0.5) + 1, 2):
        while n % i == 0:
            if is_prime(i):
                factors.add(i)
            n //= i

    res = ""
    for fac in sorted(factors):
        res += str(fac) + ", "

    return  res[:-1]


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

def process_login_data(login_info):
    """
    read login info and return a tuple of username and password
    param: login_info, string. in the format "<username>\n<password>\t"
    """
    user_details = login_info[:-1].split("\n")
    return user_details[0],user_details[1]


def close_connection(active_socket, client_address,logged_in_users_sockets_list):
    clients_messages.pop(client_address)
    logged_in_users_sockets_list.remove(active_socket)
    clients.pop(active_socket)
    disconnect_socket(active_socket)

def accept_socket(server_socket):
    client_socket, client_address = server_socket.accept()
    sockets_list.append(client_socket)
    clients[client_socket] = client_address
    print_login_message(client_socket)

def handle_new_user(user_info, active_socket, known_users_dict, logged_in_users_sockets_list):
    username, password = process_login_data(user_info)
    if username in known_users_dict and known_users_dict[username] == password:
        logged_in_users_sockets_list.append(active_socket)
        active_socket.send(f"Hi {username}, good to see you\t".encode("utf-8"))
    else:
        # the user can try again so no need to close the socket
        active_socket.send("Failed to login.\t".encode("utf-8"))

# Global vars
sockets_list = []
clients = {}  # Dictionary to keep track of client addresses
clients_messages = {}
INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647


def start_server():
    # Server Configuration
    HOST = '127.0.0.1'  # Localhost
    PORT = 1337
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print('invalid number of arguments passed')
        exit(1)
    if len(sys.argv) == 3:
        PORT = int(sys.argv[2])
    file_path = sys.argv[1]
    # loads all the users information to a dictionary
    known_users_dict = {}
    process_file(file_path,known_users_dict)

    logged_in_users_sockets_list = []

    # creates new socket
    with socket(family=AF_INET, type=SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        #Use lists to keep track of sockets
        sockets_list.append(server_socket) # List of all connected sockets
        print('server is up')
        #Main loop to handle multiple clients
        while True:
            # Use `select` to wait for socket events
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

            for active_socket in read_sockets:
                # If it's the server socket, accept a new connection
                if active_socket == server_socket:
                    accept_socket(server_socket)

                # otherwise, it's an existing client socket with data
                else:
                    # gets the address of the active socket for dictionary searches
                    client_address = clients[active_socket]

                    #recive packet
                    if client_address not in clients_messages:
                        clients_messages[client_address]=""
                    clients_messages[client_address] += active_socket.recv(1024).decode("utf-8")
                    message_builder = clients_messages[client_address]
                    # check if we got the full message
                    if message_builder != "" and message_builder[-1] == "\t":
                        # ready for new command
                        clients_messages[client_address] = ""
                        # if you're not logged in, do so. if you don't i kick u
                        if active_socket not in logged_in_users_sockets_list:
                            handle_new_user(message_builder, active_socket, known_users_dict, logged_in_users_sockets_list)
                            continue

                        # you're logged in, so you probably sent us some command
                        else:
                            # handle this case first because it requires removing stuff from data structures
                            if message_builder == 'q\t':
                                close_connection(active_socket, client_address,logged_in_users_sockets_list)
                                continue
                            message_to_send = command_handler(message_builder)
                            active_socket.send((message_to_send+"\t").encode("utf-8"))
                            #an error has occurred
                            if message_to_send[:5] == "error":
                                close_connection(active_socket, client_address, logged_in_users_sockets_list)
                                continue

                        # ready for new command
                        clients_messages[client_address] = ""



if __name__ == "__main__":
    start_server()