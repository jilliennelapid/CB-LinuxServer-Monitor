# Controller
### Facilitates communication between the GUI (view.py) and client methods (client.py)
from client import Client
import time
import threading
import json

# Class Controller that assists communication between the GUI and the client
class Controller:
    def __init__(self, _view):
        # Instantiates a client instance for access to client functions
        self.client = Client()
        self.client.set_controller(self)
        self.view = _view

        self.proceed = True
        self.statusFlag = None  # Flag for checking server connection
        self.sys_res_time = None  # Flag for setting system response time
        self.validation_result = None  # Flag for setting the result of the password validation
        self.saved_result = None

    """ Main Functionality Methods """
    # Helps make a client request to Connect to the Server
    def connect(self):
        if self.client:
            print("Activating Client...")
            self.client.activate_client()               # Attempts to connect client and server

            print("Client Activated. Testing Connection...")
            if self.client.test_connection():           # If connection successful, set flag
                time.sleep(2)
                if self.statusFlag:
                    return True
            else:
                return False

    def start_monitoring(self):
        if self.client:
            threading.Thread(target=self.client.start_stress(), daemon=True).start()

            while self.proceed:
                time.sleep(5)
                self.client.get_data()
    def stop_monitoring(self):
        if self.client:
            threading.Thread(target=self.client.stop_stress(), daemon=True).start()

    """ Methods for Sending Data back to the GUI """
    # Sends back the system response time to the GUI
    def send_sys_response(self, payload):
        self.statusFlag = 1
        self.sys_res_time = payload
        print(f"{self.statusFlag} and {self.sys_res_time}")

    def set_stats(self, payload):
        print(f"Controller received stats: {payload[:50]}...")
        try:
            # Try to parse JSON if it's already in JSON format
            data = json.loads(payload)
            self.view.update_labels(data)
        except json.JSONDecodeError:
            # If not JSON, pass it as is
            self.view.update_labels(payload)
        except Exception as e:
            print(f"Error in controller set_stats: {e}")

