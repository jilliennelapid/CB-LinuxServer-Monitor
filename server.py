# On the stress VM, create a file named socket_server.py
import socket
import json
import threading
import subprocess
import os
import time

# Define server host and port
host = '10.128.0.2'  # Listen on all interfaces
port = 3389

BUFFER_SIZE = 32786
FORMAT = 'utf-8'

threads = []


# Class MServer that handles server-side actions and data handling
class SServer:
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

                print(f"command parse success {command}")

                # Sends a success message to show a good connection between client and server
                if command == "TEST":
                    start_time = time.time()
                    response_time = round((time.time() - start_time), 8)

                    connection.send(f"OK@{response_time}".encode(FORMAT))

                elif command == "GETDATA":
                    print("made it to GETDATA")
                    filepath = "/home/jillienne_lapid/stress-testing/server_metrics.json"

                    if not os.path.exists(filepath):
                        return False

                    print("About to read data from file")

                    with open(f"{filepath}", 'r') as f:
                        # Saves the file contents to file_data
                        file_data = f.read(BUFFER_SIZE)

                    print("Data read successfully.")

                    # Dictionary send to server for upload file processing
                    return_mess = json.dumps({"filedata": file_data})

                    # Sending the data as JSON over client socket
                    threading.Thread(target=lambda: connection.send(f"STATS@{return_mess}".encode(FORMAT)),
                                     daemon=True).start()


                elif command == "START":
                    # Start stress test
                    subprocess.Popen(["/home/jillienne_lapid/stress-testing/stress_test.sh"], shell=True)
                    connection.send(json.dumps({"status": "started"}).encode('utf-8'))

                elif command == "STOP":
                    # Stop stress test
                    subprocess.Popen(["pkill -f stress-ng"], shell=True)
                    connection.send(json.dumps({"status": "stopped"}).encode('utf-8'))

            except Exception as e:
                print(f"Error handling client: {e}")
                break

        connection.close()


if __name__ == "__main__":
    # Initializes the server upon running the code
    server_socket = SServer()
    server_socket.activate_server()
