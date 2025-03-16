# Controller
### Facilitates communication between the GUI (view.py) and client methods (client.py)
from client import Client

# Class Controller that assists communication between the GUI and the client
class Controller:
    def __init__(self, _view):
        # Instantiates a client instance for access to client functions
        self.client = Client()
        self.client.set_controller(self)
        self.view = _view