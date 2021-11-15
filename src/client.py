from threading import Thread
from socket import *
import time
import sys

from server import Client_thread

# Receiving thread
class Rcv_thread(Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.is_running = True
        self.is_timed_out= False
    
    def run(self):
        while self.is_running:
            data = self.client_socket.recv(1024)
            msg = data.decode()
            if msg == '':
                self.is_timed_out = True
                break
            print(msg)
        
        self.client_socket.close()
        
    def get_is_timed_out(self):
        return self.is_timed_out

    def end(self):
        self.is_running = False

# Sending thread
class Send_thread(Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.daemon = True
    
    def run(self):
        try:
            while True:
                # parse user input
                input_string = input()
                user_input = input_string.split(" ")

                # break loop if logout command issued
                if user_input[0] == "logout":
                    if len(user_input) != 1:
                        print("Error. Invalid command")
                    else:
                        # send logout signal to server
                        self.client_socket.sendall("logout".encode('utf-8'))
                        break
                # handle whoelse 
                if user_input[0] == "whoelse":
                    if len(user_input) != 1:
                        print("Error. Invalid command")
                    else:
                        self.client_socket.sendall("whoelse".encode('utf-8'))
                # handle whoelsesince
                if user_input[0] == "whoelsesince":
                    if len(user_input) != 2:
                        print("Usage: whoelsesince <time>")
                    else:
                        if not user_input[1].isnumeric():
                            print("<time> must be an integer")
                        else:
                            self.client_socket.sendall(input_string.encode("utf-8"))
                # handle broadcast
                if user_input[0] == "broadcast": 
                    self.client_socket.sendall(input_string.encode("utf-8"))
                # handle message
                if user_input[0] == "message":
                    if len(user_input) < 3:
                        print("Usage: message <user> <message>")
                    # if recepient is self print error
                    elif user_input[2] == username:
                        print("You cannot send a message to yourself")
                    else:
                        self.client_socket.sendall(input_string.encode("utf-8"))
                # handle blocking
                if user_input[0] == "block":
                    if len(user_input) != 2:
                        print("Usage: block <username>")
                    # if attempting to block self
                    elif user_input[1] == username:
                        print("You cannot block yourself")
                    else:
                        self.client_socket.sendall(input_string.encode("utf-8"))
                
        except Exception as e:
            print(e)
    
    def timeout(self):
        raise timeout

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
        exit()

    # if username does not exist
    if message == "2":
        new_password = input("Create password: ")
        client_socket.sendall(new_password.encode("utf-8"))
        data = client_socket.recv(1024)
        message = data.decode()
        if message == "login successful":
            is_logged_in = True
        print(f"Welcome {username}")
    
    # Start the receiving thread
    rcv_thread = Rcv_thread(client_socket)
    rcv_thread.start()

    # Start the sending thread
    send_thread = Send_thread(client_socket)
    send_thread.start()

    # Start loop, checking if sending thread is active
    while True:
        # if timed out break
        if rcv_thread.get_is_timed_out():
            # stop the sending thread
            print("Connection timeout")
            break
        # if send thread finishes execution, user has logged out
        if not send_thread.is_alive():
            # call end in rcv_thread to stop listening and close the client_socket
            rcv_thread.end()
            break

    


