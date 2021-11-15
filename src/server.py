from socket import *
from threading import Thread
import time
import datetime
import sys

# Thread for a blocked username
class Blocking_thread(Thread):
    def __init__(self, username, block_duration):
        Thread.__init__(self)
        self.username = username
        self.block_duration = block_duration
    
    def run(self):
        global blocked_users
        blocked_users.append(self.username)
        time.sleep(block_duration)
        blocked_users.remove(self.username)
        

# Thread for each client connection
class Client_thread(Thread):
    def __init__(self, client_address, client_socket):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket
        self.is_logged_in = False
        self.is_alive = True
        self.username = None
        self.user_details = None
        print("New conection created for: ", client_address)

    def run(self):
        # login client 
        self.login()
        # end if login failed
        if not self.is_logged_in:
            return

        # send any messages that were sent to user when they were offline
        self.client_socket.sendall(self.user_details['messages'].encode('utf-8'))
        self.user_details['messages'] = ''

        # set timeout
        self.client_socket.settimeout(timeout)

        # Process commands
        try:
            while self.is_alive and self.is_logged_in:
                data = self.client_socket.recv(1024)
                command = data.decode()
                command_list = command.split(" ")

                # handle logout
                if command == "logout":
                    self.logout()

                if command == "whoelse":
                    self.whoelse()

                if command_list[0] == "broadcast":
                    self.broadcast(command[10:])

                if command_list[0] == "message":
                    message = ' '.join(command_list[2:])
                    self.message(command_list[1], message)

                if command_list[0] == "block":
                    self.block_user(command_list[1])
        except:
            self.timeout()       
        
        # close socket
        print("Close connection with: ", self.client_address)
        self.client_socket.close()

    # blocks user
    def block_user(self, user):
        
        # if user doesn't exist
        if user not in users:
            self.client_socket.sendall("Error: Attempting to block a username that doesn't exist".encode("utf-8"))
        # if user is already blocked
        elif user in self.user_details['blocked_users']:
            self.client_socket.sendall("Error: Username is already blocked".encode("utf-8"))
        else:
            self.user_details['blocked_users'].append(user)
            self.client_socket.sendall(f"{user} is blocked".encode("utf-8"))

    # sends message to recepient, if recepient is not active, add it to msg buffer
    def message(self, recepient, message):

        # if user doesn't exist
        if recepient not in users:
            self.client_socket.sendall(f"'{recepient}' no such user".encode("utf-8"))
            return

        # if the recepient has blocked the sender
        if self.username in users[recepient]['blocked_users']:
            self.client_socket.sendall(f"Your message could not be delivered as the recipient has blocked you".encode("utf-8"))
            return

        # if recepient is currently active
        if users[recepient]['is_active']:
            client_threads[recepient].client_socket.sendall(f"{self.username}: {message}".encode("utf-8"))
        # else append to recepients message buffer which will be sent to client once offline user logs in
        else:
            if users[recepient]['messages'] == '':
                users[recepient]['messages'] += f"{self.username}: {message}"
            else:
                users[recepient]['messages'] += f"\n{self.username}: {message}"


    # return list of active users
    def whoelse(self):
        # obtain copy of active_users list
        other_active_users = active_users.copy()
        # Remove requesting user from copied list
        other_active_users.remove(self.username)
        # Send list of active users as \n separated string
        payload = ''
        for u in other_active_users:
            # check that the user has not blocked the client
            if self.username not in users[u]['blocked_users']:
                payload += f"\n{u}"
        # Removing leading \n
        if payload != '':
            payload = payload.lstrip('\n')
        self.client_socket.sendall(payload.encode("utf-8"))
        print(f"Sent list of active users to {self.username}")

    # broadcast message to all other users
    def broadcast(self, message):
        for user in client_threads:
            # check that user has not blocked self
            if self.username in users[user]['blocked_users']:
                continue

            # don't broadcast to self
            if user != self.username:
                client_threads[user].client_socket.sendall(f"{self.username}: {message}".encode("utf-8"))
        print(f"User {self.username} broadcasted message '{message}'")

    def timeout(self):
        print(f"User {self.username} has timed out")
        # call logout function 
        self.logout()

    def logout(self):
        self.is_logged_in = False
        print(f"Logged out user {self.username}")
        # remove from list of active users and client_threads
        active_users.remove(self.username)
        client_threads.pop(self.username)

        # send logout presence notification to active users
        for user in client_threads:
            # only send presence notifications if user has not blocked user
            if self.username not in users[user]['blocked_users']:
                client_threads[user].client_socket.sendall(f"{self.username} logged out".encode("utf-8"))
        
        # set user status to inactive
        self.user_details['is_active'] = False

    def block_username(self, username):
        blocking_thread = Blocking_thread(username, block_duration)
        blocking_thread.start()
        
    # logs in client
    def login(self):
        while self.is_alive and not self.is_logged_in:
            data = self.client_socket.recv(1024)
            username_input = data.decode()

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
                f.close()
                # If username is currently blocked
                if username_input in blocked_users:
                    self.client_socket.sendall("1".encode("utf-8"))
                    print("Client inputted username is currently blocked")
                    return

                self.client_socket.sendall("0".encode("utf-8"))
                data = self.client_socket.recv(1024)
                password_input = data.decode()
                # Attempt login up to three times before blocking username for set period
                attempts = 1
                while password_input != password:
                    if attempts > 3:
                        print(f"Exhausted authentication attempts, username: {username_input} blocked for {block_duration} seconds")
                        self.client_socket.sendall("username blocked".encode("utf-8"))
                        self.block_username(username_input)
                        return
                    self.client_socket.sendall(f"Incorrect password, attempt {attempts}".encode("utf-8"))
                    data = self.client_socket.recv(1024)
                    password_input = data.decode()
                    attempts += 1

                print(f"Logged in user: '{username_input}'")
            # create new user if no matching username is found
            else:
                self.client_socket.sendall("2".encode("utf-8"))
                data = self.client_socket.recv(1024)
                password_input = data.decode()
                # append username and password to credentials
                f.write('\n' + username_input + ' ' + password_input)
                f.close()
                # add to users dict
                users[username_input] = {
                    'is_active': False,
                    'blocked_users' : [],
                    'messages' : '',
                }
                print(f"Created new user: '{username_input}'")
            
            
            # send login confirmation to client and add username to list of active users
            self.client_socket.sendall("login successful".encode("utf-8"))
            self.username = username_input
            self.user_details = users[username_input]
            self.user_details['is_active'] = True
            self.is_logged_in = True

            # send presence notifications to other active users then add new client 
            for user in client_threads:
                # only send to users who haven't blocked you
                if self.username not in users[user]['blocked_users']:
                    client_threads[user].client_socket.sendall(f"{self.username} logged in".encode("utf-8"))

            client_threads[self.username] = self
            #active_status = {'username' : self.username, 'online'}
            active_users.append(self.username)

# Return dictionary of users when server starts up
def bootstrap_users():
    users = {}
    with open('credentials.txt', 'r') as f:
        for line in f:
            credentials = line.split(' ')
            if len(credentials) == 2:
                # dictionary for each user
                user = {
                    'is_active': False,
                    'blocked_users' : [],
                    'messages' : '',
                }
                users[credentials[0]] = user
    return users

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

    # list of currently blocked users
    blocked_users = []

    # dictionary of users
    users = bootstrap_users()

    # dictionary of client threads where key = username and value = Client_thread
    client_threads = {}

    print("Starting server")
    while True:
        # listen for new client connections and create new connection threads as required
        server_socket.listen()
        client_socket, client_address = server_socket.accept()
        client_thread = Client_thread(client_address, client_socket)
        client_thread.start()

    server_socket.close()
    print('Shutting down server')
