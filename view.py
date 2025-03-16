# View
# Contains all code for drawing the GUI window and aiding its functionality
import customtkinter as ctk


# Class that defines the Main Window elements
class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None


    def set_controller(self, controller):
        self.controller = controller