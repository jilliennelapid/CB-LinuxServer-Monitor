# Client Side Code
### Requests actions for the server to do.
import socket
import json
import base64
import threading
import os
from pathlib import Path
import paramiko

# Host and Port that Client connects to
host = "34.172.196.29"
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

        print("Client Activated.")

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

                        # OK for Successful Connection
                        if mess_type == "OK":
                            print("Connection Test Successful: Server responded with 'OK'")
                            self.controller.send_sys_response(payload)

                        # Inside listen_to_server function
                        elif mess_type == "STATS":
                            print(f"Received STATS data: {payload[:50]}...")

                            try:
                                self.controller.set_stats(payload)
                            except Exception as e:
                                print(f"Error processing STATS data: {e}")

                        else:
                            print(f"Unknown message type: {mess_type}")
                    else:
                        print(f"Malformed message from server: {response}")
                except socket.error as e:
                    print(f"Error receiving server response: {e}")
                    break
            self.client.close()  # Ensure the client is closed when exiting the loop

        # Start the listener thread
        listener_thread = threading.Thread(target=listen_to_server, daemon=True)
        listener_thread.start()

    """ Methods for Client communication with Server """
    # Sends test message to server to test the connection
    def test_connection(self):
        print("Attempting to send test message")
        test_mess = {"command": "TEST"}
        self.client.send(json.dumps(test_mess).encode(FORMAT))
        return True

    def get_data(self):
        print("client data request")
        get_mess = {"command": "GETDATA"}
        self.client.send(json.dumps(get_mess).encode(FORMAT))

    def start_stress(self):
        start_mess = {"command": "START"}
        self.client.send(json.dumps(start_mess).encode(FORMAT))

    def stop_stress(self):
        stop_mess = {"command": "STOP"}
        self.client.send(json.dumps(stop_mess).encode(FORMAT))