# View
# Contains all code for drawing the GUI window and aiding its functionality
import customtkinter as ctk
from tkinter import font
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Class that defines the Main Window elements
class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None

        # Sets the aspects of the Main Window
        parent.title("Server File Share Application")
        parent.geometry("1200x720")
        parent.resizable(False, False)
        self.grid(sticky='nsew')

        """ Attributes pertaining to the whole window """
        globalFont = font.Font(family='Helvetica')
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        """ Frame containing Top Left and Top Right Frames """
        self.window_frame = ctk.CTkFrame(parent, fg_color='transparent')
        self.window_frame.grid(row=0, column=0, sticky='nsew')

        # Ensure window_frame expands properly
        self.window_frame.grid_rowconfigure(0, weight=0)  # Top frame (fixed height)
        self.window_frame.grid_rowconfigure(1, weight=1)  # Left & Right frames (expandable)
        self.window_frame.grid_columnconfigure(0, weight=1)  # Left Frame
        self.window_frame.grid_columnconfigure(1, weight=2)  # Right Frame (wider than left)

        """ Top Frame (Full Width) """
        self.top_frame = ctk.CTkFrame(self.window_frame, fg_color='transparent')
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')  # Span both columns

        self.label_FS = ctk.CTkLabel(self.top_frame, text='Server Diagnostics', font=(globalFont, 45, 'bold'))
        self.label_FS.pack(pady=10)  # Center label in the top frame

        """ Left Frame (Diagnostics) """
        self.left_frame = ctk.CTkFrame(self.window_frame, fg_color='transparent')
        self.left_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        # Configure left frame to expand within the window_frame
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_rowconfigure(3, weight=1)
        self.left_frame.grid_rowconfigure(4, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.labels = {}
        self.values = {}

        stats = ["CPU Usage", "Memory Usage", "Disk Usage", "Network Activity", "I/O Activity"]
        for i, stat in enumerate(stats):
            self.labels[stat] = ctk.CTkLabel(self.left_frame, text=f"{stat}:", font=("Helvetica", 20))
            self.labels[stat].grid(row=i, column=0, sticky='w', padx=20, pady=5)

            self.values[stat] = ctk.CTkLabel(self.left_frame, text='-', font=("Helvetica", 20, 'bold'))
            self.values[stat].grid(row=i, column=1, sticky='e', padx=(0, 30), pady=5)

        """ Right Frame (Graph Display) """
        self.right_frame = ctk.CTkFrame(self.window_frame, fg_color='transparent')
        self.right_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

        # Configure right frame to expand properly
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Create Matplotlib figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.ax.set_title("Server Performance Metrics Over Time", fontsize=35, fontweight='bold', color='blue', fontname="Helvetica")
        self.ax.set_ylim(0, 100)  # Percentage range (0-100%)
        self.ax.set_xlabel("Time", fontsize=20)
        self.ax.set_ylabel("Usage (%)", fontsize=20)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

        # Data storage for each metric
        self.data = {stat: [] for stat in stats}
        self.colors = {
            "CPU Usage": "blue",
            "Memory Usage": "red",
            "Disk Usage": "green",
            "Network Activity": "purple",
            "I/O Activity": "orange"
        }

        # Start graph updates
        # self.update_graph()


    def update_graph(self):
        # Simulating system stats (Replace with actual API/server data)
        new_stats = {
            "CPU Usage": random.randint(10, 90),
            "Memory Usage": random.randint(20, 80),
            "Disk Usage": random.randint(15, 70),
            "Network Activity": random.randint(5, 50),
            "I/O Activity": random.randint(10, 60)
        }

        for stat, value in new_stats.items():
            self.values[stat].configure(text=f"{value}%")
            self.data[stat].append(value)

            # Keep only last 20 data points
            if len(self.data[stat]) > 20:
                self.data[stat].pop(0)

        # Update the graph
        self.ax.clear()
        self.ax.set_title("Server Performance Metrics Over Time")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Usage (%)")

        for stat, values in self.data.items():
            self.ax.plot(values, color=self.colors[stat], marker="o", linestyle="-", label=stat)

        self.ax.legend()
        self.canvas.draw()

        # Refresh every 2 seconds
        self.after(2000, self.update_graph)

    # Sets the controller that view is connected to
    def set_controller(self, controller):
        self.controller = controller

# Class that defines the toplevel window for the Server Connection Status window
class InitView(ctk.CTkFrame):
    # Variable to determine if the window can be closed
    task_complete = False

    def __init__(self, parent):
        super().__init__(parent)

        self.controller = None
        self.sys_res_time = None

        # Draws the toplevel window and sets its attributes.
        self.server_connect_window = ctk.CTkToplevel(parent)
        self.server_connect_window.geometry("400x120")
        self.server_connect_window.resizable(False,False)
        self.server_connect_window.title("Server Connection")
        self.server_connect_window.transient()
        self.server_connect_window.grab_set()

        self.server_connect_window.columnconfigure(0, weight=1)

        # Label for displaying the Server Connection Status
        self.connection_label = ctk.CTkLabel(self.server_connect_window, text="Connecting to Server...", font=('Helvetica', 18))
        self.connection_label.grid(row=0, column=0, sticky='n', pady=(20,0))

        # Additional label for other information or additional status information
        self.connection_label2 = ctk.CTkLabel(self.server_connect_window, text="",
                                             font=('Helvetica', 18))
        self.connection_label2.grid(row=1, column=0, sticky='n', pady=(20, 0))

        # Additional label for other information or additional status information
        self.connection_label3 = ctk.CTkLabel(self.server_connect_window, text="",
                                              font=('Helvetica', 18))
        self.connection_label3.grid(row=2, column=0, sticky='n', pady=(20, 0))

        # Binds the close button action to on_close() function
        self.server_connect_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Ensures all widgets are rendered
        self.update_idletasks()

    # Sets the controller of the window
    def set_controller(self, controller):
        self.controller = controller

    # Function to override the close button action
    def on_close(self):
        # Allows closing if the task is complete
        if self.task_complete:
            self.server_connect_window.destroy()
        else:
            self.connection_label3.configure(text="Cannot Proceed Yet, Attempting to Connect")
            print("Task not complete. Cannot close yet.")

    """ Methods that handle attempting to Connect to the Server """
    # Calls the main thread that makes the initial server request to connect
    def connect_to_server(self):
        # Run the connection logic in a separate thread
        threading.Thread(target=self._connect_to_server_thread, daemon=True).start()

    # Handles the response of the server
    def _connect_to_server_thread(self):
        # Perform the connection logic in the thread and check the result
        if self.controller.connect():
            # Display a success if connect() was true
            # and display the system response time
            time.sleep(2)
            self.connection_label.after(0, lambda: self.connection_label.configure(text="Successfully Connected to Server!", text_color="green"))
            self.connection_label2.configure(text=f"System Response Time: {self.controller.sys_res_time}s")
            self.connection_label3.configure(text="Close Window to Proceed")
            self.task_complete = True
        else:
            # Otherwise, the connection was not successful
            time.sleep(2)
            self.connection_label.after(0, lambda: self.connection_label.configure(text="Connection Failed. Check Host IP and Port Number"))
            self.task_complete = False

    # Sets the system response time value for initView to have access to
    def set_sys_res_time(self, res_time):
        self.sys_res_time = res_time