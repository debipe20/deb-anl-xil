import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GuiManager:
    def __init__(self, root, selection_callback):
        self.root = root
        self.root.title("AMTL Uncertainty Analysis GUI")
        self.selection_callback = selection_callback  # Store the callback function
        
        # Set initial window size and background color
        self.root.geometry("1200x800")
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
        # Uncertainty Analysis tab setup
        uncertainity_analysis_tab = tk.Frame(self.tab_control, bg="#e5e5f7")
        self.tab_control.add(uncertainity_analysis_tab, text="Uncertainty Analysis")

        # Vehicle Selection Label and Dropdown
        vehicle_label = tk.Label(
            uncertainity_analysis_tab, text="Select Vehicle:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        vehicle_label.pack(pady=5)

        vehicle_options = ["2020 Tesla Model 3", "2020 Chevrolet Bolt", "2019 Nissan Leaf"]
        self.selected_vehicle = tk.StringVar()
        vehicle_dropdown = ttk.Combobox(
            uncertainity_analysis_tab, textvariable=self.selected_vehicle, 
            font=("Segoe UI", 10), values=vehicle_options
        )
        vehicle_dropdown.pack(pady=5)
        # vehicle_dropdown.set("2019 Nissan Leaf")  # Set default visible selection
        vehicle_dropdown.set("2020 Tesla Model 3")

        # Driving Cycle Label and Radiobuttons
        cycle_label = tk.Label(
            uncertainity_analysis_tab, text="Select Driving Cycle:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        cycle_label.pack(pady=(20, 5))

        self.selected_cycle = tk.StringVar(value="MCT")
        cycle_frame = tk.Frame(uncertainity_analysis_tab, bg="#e5e5f7")
        cycle_frame.pack()
        cycle_options = ["MCT", "SMCT", "WLTC"]
        for cycle in cycle_options:
            radio_button = tk.Radiobutton(
                cycle_frame, text=cycle, variable=self.selected_cycle, value=cycle,
                font=("Segoe UI", 10), bg="#e5e5f7", fg="#333", activebackground="#e5e5f7", 
                selectcolor="#a0c4ff", anchor="w"
            )
            radio_button.pack(anchor="w", padx=10)

        # Platform Selection Label and Dropdown
        platform_label = tk.Label(
            uncertainity_analysis_tab, text="Select Platform:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        platform_label.pack(pady=(20, 5))

        platform_options = ["Windows", "Linux"]
        self.selected_platform = tk.StringVar()
        platform_dropdown = ttk.Combobox(
            uncertainity_analysis_tab, textvariable=self.selected_platform, 
            font=("Segoe UI", 10), values=platform_options, state="readonly"
        )
        platform_dropdown.pack(pady=5)
        # platform_dropdown.set("Linux")  # Set default visible selection
        platform_dropdown.set("Windows") 
        # Specify Data Directory Label and Entry
        data_dir_label = tk.Label(
            uncertainity_analysis_tab, text="Specify Test File (TDMS) Data Directory:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        data_dir_label.pack(pady=(20, 5))

        # self.data_directory = tk.StringVar(value="C:\\Users\\ddas\\Documents\\Data")
        self.data_directory = tk.StringVar(value="AMTL-Test-Data")
        data_dir_entry = tk.Entry(
            uncertainity_analysis_tab, textvariable=self.data_directory, 
            font=("Segoe UI", 10), width=50
        )
        data_dir_entry.pack(pady=5)
        
        # Clamp Selection Label and Dropdown
        clamp_label = tk.Label(
            uncertainity_analysis_tab, text="Select Clamp:", 
            font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        )
        clamp_label.pack(pady=5)

        clamp_options = ["CT6843-05", "CT6844-05", "CT6846-05"]
        self.selected_clamp = tk.StringVar()
        clamp_dropdown = ttk.Combobox(
            uncertainity_analysis_tab, textvariable=self.selected_clamp, 
            font=("Segoe UI", 10), values=clamp_options
        )
        clamp_dropdown.pack(pady=5)
        clamp_dropdown.set("CT6843-05")

        # Run Analysis Button
        get_selection_button = tk.Button(
            uncertainity_analysis_tab, text="Run Uncertainty Analysis", 
            font=("Segoe UI", 10, "bold"), bg="#1a73e8", fg="#fff", activebackground="#0066cc",
            activeforeground="#fff", relief="flat", padx=10, pady=5, borderwidth=0, highlightthickness=0,
            command=self.submit_selection
        )
        get_selection_button.pack(pady=20)

        # Status Label to display success or failure message
        self.status_label = tk.Label(
            uncertainity_analysis_tab, text="", font=("Segoe UI", 10, "bold"), 
            bg="#e5e5f7", fg="#333"
        )
        self.status_label.pack(pady=10)

    def submit_selection(self):
        # Get selected values
        selected_vehicle = self.selected_vehicle.get()
        selected_cycle = self.selected_cycle.get()
        selected_platform = self.selected_platform.get()
        tdms_data_directory = self.data_directory.get()
        selected_clamp = self.selected_clamp.get()
        
        # Perform analysis with selected values
        try:
            self.selection_callback(selected_vehicle, selected_cycle, selected_platform, tdms_data_directory, selected_clamp)
            self.status_label.config(text="Successfully Completed Uncertainty Analysis!", fg="green", font=("Segoe UI", 14, "bold"))
        except Exception as e:
            self.status_label.config(text="Uncertainty Analysis Failed!", fg="red", font=("Segoe UI", 14, "bold"))
            print("Error during analysis:", e)


# Initialize the application
if __name__ == "__main__":
    def test_callback(selected_vehicle, selected_cycle):
        print("Callback received:")
        print("Selected Vehicle:", selected_vehicle)
        print("Selected Driving Cycle:", selected_cycle)
        # Simulate a delay or process
        if selected_vehicle == "Tesla Model 3":
            raise ValueError("Simulated Failure for Testing")  # Example failure for testing

    root = tk.Tk()
    app = GuiManager(root, selection_callback=test_callback)
    root.mainloop()
