# Controller
### Facilitates communication between the GUI (view.py) and client methods (client.py)
from client import Client
import time

# Class Controller that assists communication between the GUI and the client
class Controller:
    def __init__(self, _view):
        # Instantiates a client instance for access to client functions
        self.client = Client()
        self.client.set_controller(self)
        self.view = _view

        self.statusFlag = None  # Flag for checking server connection
        self.sys_res_time = None  # Flag for setting system response time
        self.validation_result = None  # Flag for setting the result of the password validation
        self.saved_result = None

    """ Main Functionality Methods """
    # Helps make a client request to Connect to the Server
    def connect(self):
        if self.client:
            print("Testing Connection...")
            self.client.activate_client()               # Attempts to connect client and server

            if self.client.test_connection():           # If connection successful, set flag
                time.sleep(2)
                if self.statusFlag:
                    return True
            else:
                return False

    # Helps make a client request to Disconnect from the Server
    #def disconnect(self):
    #    if self.client:
    #        self.client.request_server_close()
    #        self.client.close_client()

    def start_monitoring(self):
        if self.client:
            self.client.start_stress()
            time.sleep(3)
            self.client.get_data()

    """ Methods for Sending Data back to the GUI """
    # Sends back the system response time to the GUI
    def send_sys_response(self, payload):
        self.statusFlag = 1
        self.sys_res_time = payload
        print(f"{self.statusFlag} and {self.sys_res_time}")

    def set_stats(self, payload):
        self.view.update_labels(payload)

