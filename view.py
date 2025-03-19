# View
# Contains all code for drawing the GUI window and aiding its functionality
import customtkinter as ctk
from tkinter import font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import threading
import time
import json

# Class that defines the Main Window elements
class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None
        self.started = None

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
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=0)

        self.label_FS = ctk.CTkLabel(self.top_frame, text='Server Diagnostics', font=(globalFont, 45, 'bold'))
        self.label_FS.grid(row=0, column=0, sticky='w', padx=30, pady=15)

        self.start_button = ctk.CTkButton(self.top_frame, corner_radius=5, text='Start Monitoring',
                                               font=(globalFont, 18, 'bold'), fg_color='#59b1f0', hover_color='#3977e3',
                                               text_color='#fafcff', border_spacing=10, height=50,
                                               command=self.start_server_monitoring)
        self.start_button.grid(row=0, column=1, sticky='e', padx=20, pady=10)

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

        self.statVals = {stat: ctk.StringVar(value="0%") for stat in stats}  # Default to "0%

        for i, stat in enumerate(stats):
            self.labels[stat] = ctk.CTkLabel(self.left_frame, text=f"{stat}:", font=("Helvetica", 20))
            self.labels[stat].grid(row=i, column=0, sticky='w', padx=20, pady=5)

            self.values[stat] = ctk.CTkLabel(self.left_frame, textvariable=self.statVals[stat], font=("Helvetica", 20, 'bold'))
            self.values[stat].grid(row=i, column=1, sticky='e', padx=(0, 30), pady=5)

        """ Right Frame (Graph Display) """
        self.right_frame = ctk.CTkFrame(self.window_frame, fg_color='transparent')
        self.right_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

        # Configure right frame to expand properly
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Create Matplotlib figure and 5 subplots (stacked)
        self.fig, self.axs = plt.subplots(5, 1, figsize=(6, 12), dpi=100, sharex=True)

        # Set a common title
        self.fig.suptitle("Server Performance Metrics Over Time", fontsize=25, fontweight='bold', color='blue')

        # Define metric names and colors
        metrics = ["CPU Usage", "Memory Usage", "Disk Usage", "Network Activity", "I/O Activity"]
        colors = ["blue", "red", "green", "purple", "orange"]

        # Store graph properties
        self.data = {metric: [] for metric in metrics}

        # Configure each subplot
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            self.axs[i].set_title(metric, fontsize=15, fontweight="bold", color=color)
            self.axs[i].set_ylim(0, 100)  # Set y-axis limit (0-100%)
            self.axs[i].set_ylabel("Usage (%)", fontsize=12)
            self.axs[i].tick_params(axis='y', labelsize=10)
            self.axs[i].grid(True)  # Enable grid

        # Set x-axis label only for the last subplot
        self.axs[-1].set_xlabel("Time", fontsize=14)

        # Create Matplotlib canvas and integrate it with Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)


        # Start graph updates
        # self.update_graph()

    def update_graph_with_new_data(self):
        try:
            # Clear previous time points
            x_points = list(range(max(len(values) for values in self.data.values())))

            # Update each subplot
            for i, (metric, values) in enumerate(self.data.items()):
                ax = self.axs[i]
                ax.clear()

                if values:
                    # Plot the data
                    ax.plot(values, color=["blue", "red", "green", "purple", "orange"][i],
                            marker="o", linestyle="-")

                    # Configure the subplot
                    ax.set_title(metric, fontsize=15, fontweight="bold")
                    ax.set_ylim(0, 100)
                    ax.set_ylabel("Usage (%)")
                    ax.grid(True)

            # Redraw the canvas
            self.canvas.draw()
            print("Graph updated")
        except Exception as e:
            print(f"Error updating graph: {e}")

    # Sets the controller that view is connected to
    def set_controller(self, controller):
        self.controller = controller

    def start_server_monitoring(self):
        #Start stress test, data collection, and API server.
        print("Starting monitoring")
        self.controller.start_monitoring()

    def update_labels(self, data):
        print(f"View received data: {str(data)[:100]}...")

        metrics = None
        try:
            # Try to extract filedata if present
            filedata = data.get("filedata") if isinstance(data, dict) else data

            # Try to parse as JSON if it's a string
            if isinstance(filedata, str):
                try:
                    metrics = json.loads(filedata)
                    print(f"Parsed metrics into JSON: {metrics}")
                except json.JSONDecodeError:
                    print(f"Data already in JSON: {filedata[:100]}")
            else:
                metrics = filedata

            # Update the stats display
            for stat, value in metrics.items():
                print(f"{stat}, {value}")

                if stat in self.statVals:
                    try:
                        # Convert to number and format as percentage
                        numeric_value = float(value)
                        self.statVals[stat].set(f"{numeric_value:.1f}%")

                        # Update graph data
                        if stat in self.data:
                            self.data[stat].append(numeric_value)
                            if len(self.data[stat]) > 20:
                                self.data[stat].pop(0)
                    except (ValueError, TypeError):
                        print(f"Invalid value for {stat}: {value}")

            # Update graphs
            self.update_graph_with_new_data()

        except Exception as e:
            print(f"Error updating labels: {e}")

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

