#!/usr/bin/env python3
import socket
import json
import threading
import subprocess
import paramiko
import time
import os
import paramiko

# Define server host and port
HOST = '10.128.0.3'
PORT = 3389

# Define stressed VM details
STRESSED_VM_IP = '10.128.0.2'
STRESSED_VM_USER = 'jillienne_lapid'
STRESSED_VM_KEY = '~/.ssh/id_rsa'

BUFFER_SIZE = 32786
FORMAT = 'utf-8'


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.proceed = False
        self.ssh_client = None
        self.data_thread = None
        self.active_connections = []

    def setup_ssh_connection(self):
        """Establish SSH connection to the stressed VM"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Load private key if it exists, otherwise use password (not recommended)
            key_path = os.path.expanduser(STRESSED_VM_KEY)
            if os.path.exists(key_path):
                key = paramiko.RSAKey.from_private_key_file(key_path)
                self.ssh_client.connect(
                    hostname=STRESSED_VM_IP,
                    username=STRESSED_VM_USER,
                    pkey=key
                )
            else:
                # Fallback to password (should be avoided in production)
                print("WARNING: SSH key not found. Using password authentication is not recommended.")
                password = input(f"Enter password for {STRESSED_VM_USER}@{STRESSED_VM_IP}: ")
                self.ssh_client.connect(
                    hostname=STRESSED_VM_IP,
                    username=STRESSED_VM_USER,
                    password=password
                )

            print(f"SSH connection established to {STRESSED_VM_IP}")
            return True
        except Exception as e:
            print(f"SSH connection failed: {e}")
            return False

    def execute_remote_command(self, command):
        """Execute a command on the stressed VM"""
        if not self.ssh_client or not self.ssh_client.get_transport().is_active():
            if not self.setup_ssh_connection():
                return "SSH connection failed"

        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            result = stdout.read().decode(FORMAT)
            error = stderr.read().decode(FORMAT)

            if error:
                print(f"Command error: {error}")
                return error
            return result
        except Exception as e:
            print(f"Command execution failed: {e}")
            return str(e)

    def start_data_collection(self, connection):
        """Start data collection from the named pipe on the stressed VM"""
        if self.data_thread and self.data_thread.is_alive():
            return  # Already collecting data

        def collect_data():
            try:
                # Create an SSH channel for the SFTP session
                transport = self.ssh_client.get_transport()
                channel = transport.open_session()
                channel.exec_command("tail -f ~/stress-testing/stress_pipe")

                while self.proceed and connection in self.active_connections:
                    # Check if data is available to read
                    if channel.recv_ready():
                        data = channel.recv(BUFFER_SIZE).decode(FORMAT).strip()
                        if data:
                            try:
                                # Forward the data to the client
                                payload = json.dumps({"filedata": data})
                                connection.send(f"STATS@{payload}".encode(FORMAT))
                                print(f"Sent to client: {data[:50]}...")
                            except json.JSONDecodeError:
                                print(f"Invalid JSON received: {data}")
                    time.sleep(0.1)

                # Close the channel when done
                channel.close()
                print("Data collection stopped")

            except Exception as e:
                print(f"Data collection error: {e}")

        self.data_thread = threading.Thread(target=collect_data)
        self.data_thread.daemon = True
        self.data_thread.start()

    def activate_server(self):
        """Activate the server and listen for client connections"""
        try:
            self.server.bind((HOST, PORT))
            print(f"Server bound to {HOST}:{PORT}")
        except socket.error as e:
            print(f"Binding failed: {e}")
            return False

        self.server.listen(6)
        print("Server listening for connections...")

        # Setup SSH connection to stressed VM
        self.setup_ssh_connection()

        try:
            while True:
                conn, addr = self.server.accept()
                print(f"New connection from {addr}")

                self.active_connections.append(conn)
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server.close()
            if self.ssh_client:
                self.ssh_client.close()

    def handle_client(self, connection, address):
        """Handle communication with a client"""
        print(f"Handling client {address}")
        try:
            while connection in self.active_connections:
                data = connection.recv(BUFFER_SIZE)
                if not data:
                    break  # Client disconnected

                try:
                    # Parse the command from the client
                    message = json.loads(data.decode(FORMAT))
                    command = message.get("command")
                    print(f"Received command: {command}")

                    if command == "TEST":
                        # Send a response to confirm connection
                        start_time = time.time()
                        response_time = round((time.time() - start_time), 8)
                        connection.send(f"OK@{response_time}".encode(FORMAT))
                        print("Sent TEST response")

                    elif command == "START":
                        # Start the stress test and data collection on the stressed VM
                        print("Starting stress tests and data collection...")

                        # Make sure the named pipe exists
                        self.execute_remote_command("mkdir -p ~/stress-testing")
                        self.execute_remote_command(
                            "[ -p ~/stress-testing/stress_pipe ] || mkfifo ~/stress-testing/stress_pipe")

                        # Start the data collection script
                        self.execute_remote_command("nohup bash ~/stress-testing/send_data.sh > /dev/null 2>&1 &")

                        # Start the stress test script
                        self.execute_remote_command("nohup bash ~/stress-testing/stress_test.sh > /dev/null 2>&1 &")

                        # Set the flag to start data collection
                        self.proceed = True

                        # Start collecting and forwarding data
                        self.start_data_collection(connection)

                        connection.send(json.dumps({"status": "started"}).encode(FORMAT))

                    elif command == "GETDATA":
                        # Start forwarding data if not already doing so
                        print("Client requested data collection...")
                        if not self.proceed:
                            self.proceed = True
                            self.start_data_collection(connection)

                    elif command == "STOP":
                        # Stop the stress test and data collection
                        print("Stopping stress tests and data collection...")

                        # Stop the data collection by setting the flag
                        self.proceed = False

                        # Kill any running stress test processes
                        self.execute_remote_command("pkill -f stress-ng")
                        self.execute_remote_command("pkill -f send_data.sh")
                        self.execute_remote_command("pkill -f stress_test.sh")

                        connection.send(json.dumps({"status": "stopped"}).encode(FORMAT))

                    else:
                        print(f"Unknown command: {command}")

                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")

        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Clean up
            print(f"Client {address} disconnected")
            if connection in self.active_connections:
                self.active_connections.remove(connection)
            connection.close()

            # If this was the last client, stop any ongoing processes
            if not self.active_connections:
                self.proceed = False
                if self.ssh_client:
                    self.execute_remote_command("pkill -f stress-ng")
                    self.execute_remote_command("pkill -f send_data.sh")


if __name__ == "__main__":
    server = Server()
    server.activate_server()
