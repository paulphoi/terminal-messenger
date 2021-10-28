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
    if message == "1":
        while not is_logged_in:
            password = input("Enter password: ")
            client_socket.sendall(password.encode("utf-8"))
            data = client_socket.recv(1024)
            message = data.decode()
            # Repeat if password is incorrect
            if message == "Incorrect password":
                print(message)
                continue
            is_logged_in = True

    # if username does not exist
    else:
        new_password = input("Create password: ")
        client_socket.sendall(new_password.encode("utf-8"))
        data = client_socket.recv(1024)
        message = data.decode()
        if message == "login successful":
            is_logged_in = True
    
    print(f"Welcome {username}")

    while True:
        break  
    
    # Close socket
    client_socket.close()
