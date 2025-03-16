# Client Side Code
### Requests actions for the server to do.
import socket
import json
import base64
import threading
import os
from pathlib import Path

# Host and Port that Client connects to
host = "34.66.135.153"
port = 3389

BUFFER_SIZE = 32786
FORMAT = 'utf-8'

# Class Client that handles the client-side requests and communication
class Client:
    def __init__(self):
        self.controller = None

        # Creates client-side TCP socket (SOCK_STREAM) for IPv4 (AF_INET)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_time = None

    # Sets the controller for the client
    def set_controller(self, controller):
        self.controller = controller

    # Activates the client by trying to connect to the server socket
    def activate_client(self):
        try:
            # Try to connect to server with the given host address and port number
            self.client.connect((host, port))
        except socket.error as e:
            print(f"Error: {e}")
            # Return false for a socket connection error

        # Method that listens for and interprets server responses
        def listen_to_server():
            while True:
                try:
                    # Receive response from the server
                    response = self.client.recv(BUFFER_SIZE).decode(FORMAT)

                    # Exit the loop if the server closes the connection
                    if not response:
                        print("Server closed the connection.")
                        break

                    # Break up the received message by the divider "@"
                    if "@" in response:
                        mess_type, payload = response.split("@")
