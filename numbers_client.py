#!/usr/bin/env python3
import ipaddress
import re
from socket import *
import sys

#globals
INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647

def recv_all_as_string(client_socket):
    """
        Receives data from the socket until a tab character ('\t') is encountered.
        Ensures complete message retrieval in case of partial packets.
        Closes the connection if no data is received.
    """
    msg = ''
    while msg == '' or msg[-1] != '\t':
        tmp = client_socket.recv(1024).decode('utf-8')
        # Handle FIN packet case
        if not tmp:
            client_socket.close()
            return ''
        msg += tmp
    return msg[:-1]


def validate_login_input(user, pw):
    """
        Validates login input format.
        Expects `user` to start with "User: " and `pw` to start with "Password: ".
    """
    return user[0:6] == "User: " and pw[0:10] == "Password: "

def validate_hostname(hostname):
    """
       Validates if the given hostname is either a valid IP address or a domain name.
    """
    # Validate if it's an IP address
    try:
        ipaddress.ip_address(hostname)
        return True  # It's a valid IP address
    except ValueError:
        pass

    # Validate if it's a domain name
    # RFC 1034/1035-compliant hostname regex
    domain_regex = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,6})+$')
    if domain_regex.match(hostname) or hostname == 'localhost':
        return True  # It's a valid domain name
    return False

def validate_port(port):
    """
       Validates if the port is a valid integer and within the range 0–65535.
       Return a boolean whether the port is valid or not, and prints an error message accordingly.
    """
    try:
        # Convert the port to an integer
        port = int(port)
        # Check if it's within the valid range
        if not 0 <= port <= 65535:
            print("error: port number must be between 0 and 65535.")
            return False
        return True
    except ValueError:
        print("error: port number must be an integer.")
        return False

def validate_int(num):
    """
       Validates if a given number is within the range of a 32-bit integer.
       Returns True for valid integers, False otherwise.
    """
    try:
        return INT32_MIN <= int(num) <= INT32_MAX
    except ValueError:
        return False

def validate_max(numbers):
    """
        Validates that all numbers that was given in a
         space-separated string are valid 32-bit integers.
    """
    return all(validate_int(num) for num in numbers.split(" "))

def parsing_sender(client_socket, message):
    """
        Sends a formatted message (appending a tab character) through the client socket.
    """
    client_socket.sendall((message+"\t").encode('utf-8'))

def handle_error(client_socket, message =""):
    """
        Handles errors by printing the error message,
        and closing the socket.
    """
    print(message + "\n shutting down connection")
    client_socket.close()

def validate_op(op):
    """
        Validates if the operator is one of the supported arithmetic operators: ^, /, *, -, +.
    """
    return op in ("^", "/", "*", "-", "+")

def handle_calc_request(client_socket):
    """
        Handles user requests for calculation methods
        Sends requests to the server and displays responses.
        Closes the connection on errors.
    """
    user_request = input()
    if user_request[:5] == "max: ": # Maximum of numbers
        if not validate_max(user_request[6:-1]) or user_request[5] != "(" or user_request[-1] != ")":
            handle_error(client_socket, "error: one of the numbers isn't 32 integer")
            exit(1)
        parsing_sender(client_socket,"m:"+user_request[5:])
        print("the maximum is: " + recv_all_as_string(client_socket) +".")

    elif user_request[:9] == "factors: ": # Prime factorization
        if not validate_int(user_request[9:]):
            handle_error(client_socket, "error: the number isn't 32 integer")
            exit(1)
        parsing_sender(client_socket, "f:"+user_request[9:])
        print( "the prime factors of " + user_request[9:] +
               " are: " + recv_all_as_string(client_socket) + '.')

    elif user_request[:11] == "calculate: ":  # Arithmetic operations
        calc_data = user_request[11:].split(" ")
        if (not validate_int(calc_data[0]) or not validate_int(calc_data[2])
                or (calc_data[1] == "/" and calc_data[2] == "0")
                or not validate_op(calc_data[1])):
            handle_error(client_socket, "error: There is a problem with the input numbers")
            exit(1)
        parsing_sender(client_socket, "c:"+user_request[11:])
        response = recv_all_as_string(client_socket)
        if response[:7] == "error: ":
            print(response)
        else:
            print( "response: " + response + ".")


    elif user_request == "quit":  # Quit command
        parsing_sender(client_socket, "q")
        client_socket.close()
        exit(1)

    else:
        handle_error(client_socket, "error: illegal command")
        exit(1)


def start_client():
    HOST_NAME = 'localhost'
    PORT = 1337

    # args validation
    if len(sys.argv) > 3:
        print('invalid number of arguments passed')
        exit(1)
    if len(sys.argv) >= 2:
        HOST_NAME = sys.argv[1]
        if not validate_hostname(HOST_NAME):
            print("error: invalid_hostname")
            exit(1)
        if len(sys.argv) == 3:
            PORT = int(sys.argv[2])
            if not validate_port(PORT):
                exit(1)

    # Establish connection
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST_NAME, PORT))

    welcome_msg = recv_all_as_string(client_socket)
    if welcome_msg != 'Welcome! Please log in.':
        handle_error(client_socket, 'Did not receive proper welcoming message from server')
        exit(1)
    print(welcome_msg)
    # Login loop
    successful_login = False
    while True:
        user_input = input()
        password_input = input()
        if not validate_login_input(user_input, password_input):
            handle_error(client_socket, "Unexpected login format")
            break
        user_input = user_input[6:]
        password_input = password_input[10:]
        login_msg = user_input + '\n' + password_input + '\t'
        client_socket.sendall(login_msg.encode('utf-8'))

        response = recv_all_as_string(client_socket)

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
        handle_calc_request(client_socket)


if __name__ == "__main__":
    start_client()