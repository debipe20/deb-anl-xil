import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Create the main window
root = tk.Tk()
root.title("Driver-In-Loop Test Status")
root.geometry("900x700")  # Increased height to fit the logo

# Title Label
title_label = tk.Label(root, text="Driver-In-Loop Test Status", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

# Create Frames
spat_frame = tk.Frame(root, bd=2, relief="groove")
host_frame = tk.Frame(root, bd=2, relief="groove")
remote_frame = tk.Frame(root, bd=2, relief="groove")
map_frame = tk.Frame(root, bd=2, relief="groove")

spat_frame.pack(fill="x", padx=5, pady=5)
host_frame.pack(fill="x", padx=5, pady=5)
remote_frame.pack(fill="x", padx=5, pady=5)
map_frame.pack(fill="x", padx=5, pady=5)

# SPaT Data Section
tk.Label(spat_frame, text="SPaT Data", font=("Arial", 12, "bold")).pack()
tk.Label(spat_frame, text="Min End Time: --   Max End Time: --").pack()

# Host Vehicle Data
tk.Label(host_frame, text="Host Vehicle", font=("Arial", 12, "bold")).pack()
host_info = [
    "Temp ID: -1898502772", "Vehicle Type: Transit", "Speed: 39 mph",
    "Latitude: 32.2358890", "Longitude: -110.9540020", "Elevation: 740.2",
    "Heading: 89.454", "Lane: 13"
]
for item in host_info:
    tk.Label(host_frame, text=item).pack()

# Remote Vehicles Table
tk.Label(remote_frame, text="Remote Vehicles", font=("Arial", 12, "bold")).pack()
remote_table = ttk.Treeview(remote_frame, columns=("Vehicle", "Time", "Type", "Latitude", "Longitude", "Elevation", "Heading", "Speed"), show="headings")
for col in remote_table["columns"]:
    remote_table.heading(col, text=col)
    remote_table.column(col, width=80)
remote_table.pack()

# Available Maps Table
tk.Label(map_frame, text="Available Maps", font=("Arial", 12, "bold")).pack()
map_table = ttk.Treeview(map_frame, columns=("Intersection", "Descriptive Name", "Active", "Age"), show="headings")
for col in map_table["columns"]:
    map_table.heading(col, text=col)
    map_table.column(col, width=100)
map_table.insert("", "end", values=(26379, "speedway-mountain", "True", 1.0))
map_table.pack()

# Load and Display Logo (Fixed)
try:
    # Get absolute path to the image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "images", "ANL-Logo.png")

    # Ensure the file exists before loading
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    # Load and resize image
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((250, 80))  # Resize for better fit
    logo_tk = ImageTk.PhotoImage(logo_img)

    # Display Image
    logo_label = tk.Label(root, image=logo_tk)
    logo_label.image = logo_tk  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=10)
except Exception as e:
    tk.Label(root, text="Error loading logo: " + str(e), fg="red").pack()

# Run GUI
root.mainloop()
