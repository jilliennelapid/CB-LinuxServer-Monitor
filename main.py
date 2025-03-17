# Main
# Initiates the main app call and starts all essential parts of the program
from view import View, InitView
from controller import Controller

import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        # Initializes the GUI main window
        super().__init__()

        # Expands upon the main window in the View class
        view = View(self)

        # Initializes the controller
        self.controller = Controller(view)
        # Sets the controller of the view
        View.set_controller(view, self.controller)

        # Creates window to do the server connection
        initView = InitView(self)
        InitView.set_controller(initView, self.controller)
        self.update_idletasks()
        # Window tries to connect to the server
        InitView.connect_to_server(initView)


        # Handles the closing of the main window
        #self.protocol("WM_DELETE_WINDOW", self.on_close)

    #def on_close(self):
    #    self.controller.disconnect()
    #    self.destroy()

if __name__ == '__main__':
    # Creates an object from class App, which also creates the window using tkinter module
    app = App()
    app.mainloop()
