import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GuiManager:
    def __init__(self, root, selection_callback):
        self.root = root
        self.root.title("Vehicle Simulation GUI")
        self.selection_callback = selection_callback  # Store the callback function
        
        # Set initial window size and background color
        self.root.geometry("800x600")
        self.root.configure(bg="#e5e5f7")  # Light pastel background
        
        # Set up tab control with style
        style = ttk.Style()
        style.theme_use("clam")  # Clam theme for a modern look
        style.configure("TNotebook", background="#e5e5f7", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(10, 5))
        style.map("TNotebook.Tab", background=[("selected", "#a0c4ff")], foreground=[("selected", "#000")])
        
        self.tab_control = ttk.Notebook(self.root)
        
        # Initialize tabs
        self.setup_home_tab()
        self.setup_uncertainity_analysis_tab()
        
        # Pack the tab control into the main window
        self.tab_control.pack(expand=1, fill="both")
    
    def setup_home_tab(self):
        # Home tab with logo display
        home_tab = tk.Frame(self.tab_control, bg="#dbe9f5")
        self.tab_control.add(home_tab, text="Home")
        
        # Load and display the logo
        logo_path = "images/ANL-Logo.png"
        image = Image.open(logo_path)
        image = image.resize((300, 100), Image.LANCZOS)
        logo = ImageTk.PhotoImage(image)
        
        logo_label = tk.Label(home_tab, image=logo, bg="#dbe9f5")
        logo_label.image = logo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=20)
        
        # Welcome message below the logo
        welcome_label = tk.Label(
            home_tab, text="Welcome to AMTL Uncertainty Analysis Tool", 
            font=("Segoe UI", 20), bg="#dbe9f5", fg="#1a73e8"
        )
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Note at the bottom
        note_label = tk.Label(
            home_tab, text="Analysis will follow SAE J1634 Standards", 
            font=("Segoe UI", 10, "italic"), bg="#dbe9f5", fg="#4c4f56"
        )
        note_label.pack(side="bottom", pady=10)

    def setup_uncertainity_analysis_tab(self):
        # Vehicle Selection tab
        uncertainity_analysis_tab = tk.Frame(self.tab_control, bg="#e5e5f7")
        self.tab_control.add(uncertainity_analysis_tab, text="Uncertainity Analysis")
        
        # Dropdown menu for vehicle selection
        vehicle_label = tk.Label(
            uncertainity_analysis_tab, text="Select Vehicle:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        vehicle_label.pack(pady=5)

        vehicle_options = ["Tesla Model 3", "2020 Chevrolet Bolt", "2019 Nissan Leaf"]
        self.selected_vehicle = tk.StringVar()
        vehicle_dropdown = ttk.Combobox(
            uncertainity_analysis_tab, textvariable=self.selected_vehicle, 
            font=("Segoe UI", 10), values=vehicle_options
        )
        vehicle_dropdown.pack(pady=5)
        vehicle_dropdown.configure(foreground="#1a73e8", background="#fff")  # Accent color for dropdown
        
        # Center the cycle label below the vehicle label
        cycle_label = tk.Label(
            uncertainity_analysis_tab, text="Select Driving Cycles:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        cycle_label.pack(pady=(20, 5))

        # Create a frame to hold the cycle checkboxes and center it
        cycle_frame = tk.Frame(uncertainity_analysis_tab, bg="#e5e5f7")
        cycle_frame.pack()

        self.cycle_vars = {}
        cycles = ["UDDS", "HWY", "US06", "SSS 65mph"]
        for cycle in cycles:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                cycle_frame, text=cycle, variable=var, 
                font=("Segoe UI", 10), bg="#e5e5f7", fg="#333", 
                activebackground="#a0c4ff", selectcolor="#1a73e8", anchor="w", relief="flat"
            )
            checkbox.pack(anchor="w", padx=10)
            self.cycle_vars[cycle] = var
        
        # Button to get selected vehicle and cycles and trigger the callback
        get_selection_button = tk.Button(
            uncertainity_analysis_tab, text="Run Uncertainity Analysis", 
            font=("Segoe UI", 10, "bold"), bg="#1a73e8", fg="#fff", activebackground="#0066cc",
            activeforeground="#fff", relief="flat", padx=10, pady=5, borderwidth=0, highlightthickness=0,
            command=self.submit_selection
        )
        get_selection_button.pack(pady=20)

    def submit_selection(self):
        # Get selected vehicle
        selected_vehicle = self.selected_vehicle.get()
        
        # Get selected cycle
        selected_cycle = [cycle for cycle, var in self.cycle_vars.items() if var.get()]
        
        # Call the callback function with the selections
        self.selection_callback(selected_vehicle, selected_cycle)


# Initialize the application
if __name__ == "__main__":
    def test_callback(selected_vehicle, selected_cycle):
        print("Callback received:")
        print("Selected Vehicle:", selected_vehicle)
        print("Selected Driving Cycles:", selected_cycle)

    root = tk.Tk()
    app = GuiManager(root, selection_callback=test_callback)
    root.mainloop()
