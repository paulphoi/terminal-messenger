from ctypes import memset
from socket import *
import sys

if __name__ == '__main__':
    # When command line ags are invalid
    if len(sys.argv) != 2:
        print("Usage: python3 client.py server_port")
        exit()

    # Process command line arguments
    server_port = int(sys.argv[1])

    # create new socket for client
    client_socket = socket(AF_INET, SOCK_STREAM)
    server_address = ("127.0.0.1", server_port)
    client_socket.connect(server_address)
    print("Connected to server: ", server_address)
    
    # process login
    username = input("Enter username: ")
    client_socket.sendall(username.encode("utf-8"))
    data = client_socket.recv(1024)
    message = data.decode()
    is_logged_in = False

    # if username exists
    if message == "0":
        while not is_logged_in:
            password = input("Enter password: ")
            client_socket.sendall(password.encode("utf-8"))
            data = client_socket.recv(1024)
            message = data.decode()
            # Repeat if password is incorrect
            if message != "login successful":
                # Quit if more than 3 consecutive incorrect attempts
                if message == "username blocked":
                    client_socket.close()
                    print("Too many incorrect attempts, username blocked")
                    exit()
                print(message)
                continue
            is_logged_in = True
        print(f"Welcome {username}")

    # if username is currently blocked
    if message == "1":
        print("Entered username is currently blocked")

    # if username does not exist
    if message == "2":
        new_password = input("Create password: ")
        client_socket.sendall(new_password.encode("utf-8"))
        data = client_socket.recv(1024)
        message = data.decode()
        if message == "login successful":
            is_logged_in = True
        print(f"Welcome {username}")
    
    

    while True and is_logged_in:
        user_input = input()

        # break loop if logout command issued
        if (user_input == "logout"):
            is_logged_in = False
            # send logout signal to server
            client_socket.sendall("logout".encode('utf-8'))


    # Close socket
    client_socket.close()
