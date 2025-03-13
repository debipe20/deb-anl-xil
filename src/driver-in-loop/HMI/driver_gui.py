import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class DriverInLoopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Driver-In-Loop Test Status")
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

        self.spat_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.host_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.remote_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)
        self.lead_vehicle_frame = tk.Frame(self.root, bd=4, relief="ridge", bg=frame_bg)

        # Arrange in Grid (Left Side)
        self.spat_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.host_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Arrange in Grid (Right Side)
        self.remote_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.lead_vehicle_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        # SPaT Data Section
        tk.Label(self.spat_frame, text="SPaT Data", font=("Helvetica", 18, "bold"), fg=header_color, bg=frame_bg).pack()
        self.spat_label = tk.Label(self.spat_frame, text="Min End Time: --   Max End Time: --",
                                   font=("Helvetica", 14), fg=text_color, bg=frame_bg)
        self.spat_label.pack()

        # Load SPaT Images
        self.load_spat_images()
        self.spat_image_label = tk.Label(self.spat_frame, image=self.spat_images["Dark"], bg=frame_bg)
        self.spat_image_label.pack()

        # Host Vehicle Data
        tk.Label(self.host_frame, text="Host Vehicle", font=("Helvetica", 18, "bold"), fg=header_color, bg=frame_bg).pack()
        self.host_labels = []
        host_info = [
            "Temp ID: -1898502772", "Vehicle Type: Transit", "Speed: 39 mph",
            "Latitude: 32.2358890", "Longitude: -110.9540020", "Elevation: 740.2",
            "Heading: 89.454", "Lane: 13"
        ]
        for item in host_info:
            label = tk.Label(self.host_frame, text=item, font=("Helvetica", 14), fg=text_color, bg=frame_bg)
            label.pack()
            self.host_labels.append(label)

        # Remote Vehicles Table
        tk.Label(self.remote_frame, text="Remote Vehicles", font=("Helvetica", 18, "bold"), fg=header_color, bg=frame_bg).pack()
        self.remote_table = ttk.Treeview(self.remote_frame, columns=("Vehicle", "Time", "Type", "Latitude", "Longitude", "Elevation", "Heading", "Speed"), show="headings")
        for col in self.remote_table["columns"]:
            self.remote_table.heading(col, text=col)
            self.remote_table.column(col, width=90)
        self.remote_table.pack()

        # Lead Vehicle Information Section
        tk.Label(self.lead_vehicle_frame, text="Lead Vehicle Information", font=("Helvetica", 18, "bold"),
                 fg=header_color, bg=frame_bg).pack()
        self.lead_vehicle_labels = []
        lead_info = [
            "Relative Speed: --", "Distance Gap: --", "Ego Speed: --",
            "Lead Speed: --", "Distance to Intersection: --"
        ]
        for item in lead_info:
            label = tk.Label(self.lead_vehicle_frame, text=item, font=("Helvetica", 14), fg=text_color, bg=frame_bg)
            label.pack()
            self.lead_vehicle_labels.append(label)

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

    def update_spat_data(self, min_end, max_end, signal_color="Dark"):
        """Updates SPaT data dynamically."""
        self.spat_label.config(text=f"Min End Time: {min_end}   Max End Time: {max_end}")
        if signal_color in self.spat_images:
            self.spat_image_label.config(image=self.spat_images[signal_color])

    def update_host_info(self, new_info):
        """Updates host vehicle information dynamically."""
        for i, item in enumerate(new_info):
            if i < len(self.host_labels):
                self.host_labels[i].config(text=item)

    def update_remote_table(self, new_data):
        """Clears and updates remote vehicle table."""
        for row in self.remote_table.get_children():
            self.remote_table.delete(row)
        for item in new_data:
            self.remote_table.insert("", "end", values=item)

    def update_lead_vehicle_info(self, lead_info):
        """Updates lead vehicle data dynamically."""
        for i, item in enumerate(lead_info):
            if i < len(self.lead_vehicle_labels):
                self.lead_vehicle_labels[i].config(text=item)



    