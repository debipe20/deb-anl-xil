"""
DriverInLoopGUI.py
------------------
Graphical User Interface (GUI) for displaying real-time vehicle and SPaT (Signal Phase and Timing) data in the 
Driver-In-Loop (DIL) Human-Machine Interface (HMI).

Features:
- Displays lead and ego vehicle data (ID, model, speed, GPS coordinates, elevation, heading).
- Shows SPaT signal information with real-time updates.
- Provides a summary of distance gap, lead speed, and ego speed.
- Loads and displays an ANL logo at the bottom of the interface.
- Dynamically updates vehicle and SPaT data based on received messages.

Dependencies:
- `tkinter` for GUI components.
- `PIL` for image handling.
- `os` for file path operations.

Author: Debashis Das
Organization: Argonne National Laboratory (Transportation and Power Systems Division)
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class DriverInLoopGUI:
    """
    A GUI class for visualizing vehicle and SPaT data in real time.

    Attributes:
        root (tk.Tk): The main application window.
        title_label (tk.Label): Label for the GUI title.
        lead_labels (list): Labels displaying lead vehicle data.
        ego_labels (list): Labels displaying ego vehicle data.
        spat_label (tk.Label): Label displaying SPaT timing data.
        summary_labels (list): Labels displaying summary information.
        spat_images (dict): Dictionary storing SPaT signal images.

    Methods:
        load_logo(): Loads and displays the ANL logo.
        load_spat_images(): Loads SPaT signal images.
        update_spat_data(min_end, max_end, signal_color): Updates SPaT information dynamically.
        update_ego_info(new_info): Updates ego vehicle data dynamically.
        update_lead_table(new_data): Updates lead vehicle table dynamically.
        update_summary_info(summary_info): Updates summary data dynamically.
    """
    def __init__(self, root):
        """Initializes the GUI and sets up the layout."""
        self.root = root
        self.root.title("AMTL ViL HMI")
        self.root.geometry("1000x700")  # Adjusted size
        self.root.configure(bg="#2E2E2E")  # Dark gray background

        # Configure Grid Layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=0)

        # Title Label
        self.title_label = tk.Label(self.root, text="Driver-In-Loop Test Status", font=("Helvetica", 20, "bold"),
                                    fg="white", bg="#2E2E2E")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="n")

        # Create Frames with Backgrounds
        frame_bg = "#3E3E3E"  # Dark Gray
        header_color = "#FFD700"  # Gold color for section headers
        text_color = "white"
        summary_color = "cyan"

        self.spat_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.ego_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.lead_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.summary_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)

        # Arrange in Grid (Left Side)
        self.lead_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.ego_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Arrange in Grid (Right Side)
        self.spat_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.summary_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        # Lead Vehicles Table
        """If you are looking for inserting table"""
        # tk.Label(self.lead_frame, text="Lead Vehicles", font=("Helvetica", 18, "bold"), fg=header_color, bg=frame_bg).pack()
        # self.lead_table = ttk.Treeview(self.lead_frame, columns=("Vehicle", "Time", "Type", "Latitude", "Longitude", "Elevation", "Heading", "Speed"), show="headings")
        # for col in self.lead_table["columns"]:
        #     self.lead_table.heading(col, text=col)
        #     self.lead_table.column(col, width=90)
        # self.lead_table.pack()
        
        tk.Label(self.lead_frame, text="Lead Vehicle", font=("Helvetica", 32, "bold"), fg=header_color, bg=frame_bg).pack()
        self.lead_labels = []
        lead_info = [
            "Vehicle ID: -1898502772", "Vehicle Model: Simulated", "Speed: 39 mph",
            "Latitude: 32.2358890", "Longitude: -110.9540020", "Elevation: 740.2",
            "Heading: 89.454"
        ]
        for item in lead_info:
            label = tk.Label(self.lead_frame, text=item, font=("Helvetica", 20), fg=text_color, bg=frame_bg)
            label.pack()
            self.lead_labels.append(label)

        # Ego Vehicle Data
        tk.Label(self.ego_frame, text="Ego Vehicle", font=("Helvetica", 32, "bold"), fg=header_color, bg=frame_bg).pack()
        self.ego_labels = []
        ego_info = [
            "Vehicle ID: -1898502772", "Vehicle Model: Hyundai Ioniq5", "Speed: 39 mph",
            "Latitude: 32.2358890", "Longitude: -110.9540020", "Elevation: 740.2",
            "Heading: 89.454"
        ]
        for item in ego_info:
            label = tk.Label(self.ego_frame, text=item, font=("Helvetica", 20), fg=text_color, bg=frame_bg)
            label.pack()
            self.ego_labels.append(label)
    
        # SPaT Data Section
        tk.Label(self.spat_frame, text="SPaT Data", font=("Helvetica", 32, "bold"), fg=header_color, bg=frame_bg).pack()
        self.spat_label = tk.Label(self.spat_frame, text="Min End Time: --   Max End Time: --",
                                   font=("Helvetica", 20), fg=text_color, bg=frame_bg)
        self.spat_label.pack()

        # Load SPaT Images
        self.load_spat_images()
        self.spat_image_label = tk.Label(self.spat_frame, image=self.spat_images["Dark"], bg=frame_bg)
        self.spat_image_label.pack()

        # Summary Information Section
        tk.Label(self.summary_frame, text="Summary Information", font=("Helvetica", 32, "bold"),
                 fg=header_color, bg=frame_bg).pack()
        self.summary_labels = []
        summary_info = [
            "Distance Gap: 10 m", "Desired Distance Gap: 10 m",
            "Lead Speed: 0 mph", "Ego Speed: 0 mph"
        ]
        for item in summary_info:
            label = tk.Label(self.summary_frame, text=item, font=("Helvetica", 24), fg=summary_color, bg=frame_bg)
            label.pack()
            self.summary_labels.append(label)

        # Load and Display Logo (Without Changing Background)
        self.load_logo()

    def load_logo(self):
        """Loads and displays the ANL logo at the bottom."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "images", "ANL-Logo.png")

            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((250, 80))
                self.logo_tk = ImageTk.PhotoImage(logo_img)
                self.logo_label = tk.Label(self.root, image=self.logo_tk, bg="#2E2E2E")
                self.logo_label.grid(row=3, column=0, columnspan=2, pady=5)
        except Exception as e:
            tk.Label(self.root, text=f"Error loading logo: {e}", fg="red", bg="#2E2E2E").grid(row=3, column=0, columnspan=2, pady=5)
            
    def load_spat_images(self):
        """Loads SPaT signal images."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.spat_images = {}
        image_files = {"Dark": "Dark.png", "Green": "Green.png", "Red": "Red.png", "Yellow": "Yellow.png"}
        for key, filename in image_files.items():
            img_path = os.path.join(script_dir, "images", filename)
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((50, 150))
                self.spat_images[key] = ImageTk.PhotoImage(img)

    def update_lead_table(self, new_data):
        """Clears and updates lead vehicle table."""
        """If you are looking for inserting table"""
        # for row in self.lead_table.get_children():
        #     self.lead_table.delete(row)
        # for item in new_data:
        #     self.lead_table.insert("", "end", values=item)
        
        for i, item in enumerate(new_data):
            if i < len(self.lead_labels):
                self.lead_labels[i].config(text=item)    

    def update_ego_info(self, new_info):
        """Updates ego vehicle information dynamically"""
        for i, item in enumerate(new_info):
            if i < len(self.ego_labels):
                self.ego_labels[i].config(text=item)
                
    def update_spat_data(self, min_end, max_end, signal_color="Dark"):
        """Updates SPaT data dynamically"""
        self.spat_label.config(text=f"Min End Time: {min_end}   Max End Time: {max_end}")
        if signal_color in self.spat_images:
            self.spat_image_label.config(image=self.spat_images[signal_color])

    def update_summary_info(self, summary_info):
        """Updates summary data dynamically"""
        for i, item in enumerate(summary_info):
            if i < len(self.summary_labels):
                self.summary_labels[i].config(text=item)



    