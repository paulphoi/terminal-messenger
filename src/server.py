from socket import *
import sys

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
    server_socket.connect(('127.0.0.1', port))

    print("Starting server")
    while True:
        break

    server_socket.close()
