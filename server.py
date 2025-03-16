"""
# Server Side Code
### Processes Requests and performs desired actions.
### Occasionally returns data or confirmation to client-side
import socket
import json
import os
import time
import threading
import base64
import shutil
import bcrypt
from datetime import datetime

# Host and Port that Server Binds to
host = "10.128.0.3"
port = 3389

BUFFER_SIZE = 32786
dashes = '---->'
FORMAT = 'utf-8'

threads = []

# Class Server that handles server-side actions and data handling
class Server:
    def __init__(self):
        # Creates server-side TCP socket (SOCK_STREAM) with IPv4 (AF_INET)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Activates the server by binding the server to the VM instance IP address and given port
    def activate_server(self):
        try:
            # Try to bind host to the given host address and port number.
            self.server.bind((host, port))
            print("Server Bind Success!")
        except socket.error:
            return False

        # After successfully binding server, allow server to listen for messages (up to 6)
        self.server.listen(6)

        # Server will continuously accept messages until program ends
        while True:
            conn, addr = self.server.accept()

            # Threading to handle multiple client server request
            t = threading.Thread(target=self.decode_client, args=(conn,))
            t.start()
            threads.append(t)

    # Decodes the Request Messages sent from the Client
    def decode_client(self, connection):
        while True:
            try:
                # Receive command message on server side
                command_mess = connection.recv(BUFFER_SIZE)

                # Decode and parse JSON
                decode_mess = json.loads(command_mess.decode(FORMAT))

                # Get the desired command out of the JSON message
                command = decode_mess["command"]

                # If a file name is provided, save that data
                try:
                    filename = decode_mess["filename"]
                except KeyError:
                    filename = ""

                # Sends a success message to show a good connection between client and server
                if command == "TEST":
"""