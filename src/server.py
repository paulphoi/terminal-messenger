from socket import *
from threading import Thread;
import sys

# Thread for each client connection
class Client_thread(Thread):
    def __init__(self, client_address, client_socket):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket
        self.is_logged_in = False
        self.is_alive = True
        print("New conection created for: ", client_address)

    def run(self):
        # login client 
        self.login()
            
    
    # logs in client
    def login(self):
        while self.is_alive and not self.is_logged_in:
            data = self.client_socket.recv(1024)
            username_input = data.decode()

            if username_input == '':
                self.is_alive = False
                print("===== the user disconnected - ", client_address)
                break

            # open credentials.txt
            f = open("credentials.txt", "r+")
            password = None
            existing_username = False
            for line in f:
                usrname_password = line.split()
                if len(usrname_password) == 2 and usrname_password[0] == username_input:
                    password = usrname_password[1]
                    existing_username = True
                    break
            
            # send confirmation message to client if matching username is found
            if existing_username:
                self.client_socket.sendall("1".encode("utf-8"))
                data = self.client_socket.recv(1024)
                password_input = data.decode()
                # Attempt login up to three times before blocking username for set period
                while password_input != password:
                    self.client_socket.sendall("Incorrect password".encode("utf-8"))
                    data = self.client_socket.recv(1024)
                    password_input = data.decode()
                    f.close()
                print(f"Logged in user: '{username_input}'")
            # create new user if no matching username is found
            else:
                self.client_socket.sendall("0".encode("utf-8"))
                data = self.client_socket.recv(1024)
                password_input = data.decode()
                # append username and password to credentials
                f.write('\n' + username_input + ' ' + password_input)
                f.close()
                print(f"Created new user: '{username_input}'")
            
            
            # send login confirmation to client and add username to list of active users
            client_socket.sendall("login successful".encode("utf-8"))
            print(username_input)
            self.is_logged_in = True
            global active_users
            active_users.append(username_input)
                        

if __name__ == '__main__':
    # When command line ags are invalid
    if len(sys.argv) != 4:
        print("Usage: python3 server.py server_port block_duration timeout")
        exit()

    # Process command line arguments
    port = int(sys.argv[1])
    block_duration = float(sys.argv[2])
    timeout = float(sys.argv[3])

    # create listening socket
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))

    # list of active users
    active_users = []

    print("Starting server")
    while True:
        # listen for new client connections and create new connection threads as required
        server_socket.listen()
        client_socket, client_address = server_socket.accept()
        client_thread = Client_thread(client_address, client_socket)
        client_thread.start()

    server_socket.close()
    print('Shutting down server')
