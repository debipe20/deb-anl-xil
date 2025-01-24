"""
**********************************************************************************

GuiManager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
The `GuiManager` class provides a Graphical User Interface (GUI) for the AMTL 
Uncertainty Analysis Tool. It is designed to streamline the process of vehicle 
analysis by offering a tabbed interface for configuration, parameter management, 
and running uncertainty analysis.

Key Features:
-------------
- **Tabbed Layout**:
  - **Home Tab**: Displays a welcome message and logo.
  - **Parameter Tab**: Allows users to manage configuration parameters, including 
    file details, summary data fields, and Hioki CAN fields.
  - **Uncertainty Analysis Tab**: Enables vehicle selection, drive cycle selection, 
    and execution of analysis with real-time feedback.

- **Dynamic Configurability**:
  - Editable entries for file paths, data fields, and analysis parameters.
  - Automatic saving of configuration files with UTF-8 encoding.

- **User Feedback**:
  - Real-time status messages for analysis success or failure.
  - Confirmation message for successful saving of configurations.

- **Error Handling**:
  - Captures and displays errors during saving or analysis execution.

Methods:
--------
- __init__(self, root, selection_callback, config_path): 
  Initializes the GUI, loads configuration, and sets up the tabs.

- setup_home_tab(self): 
  Configures the Home tab with a logo and introductory messages.

- setup_parameter_tab(self): 
  Configures the Parameter tab with sub-tabs for managing configurations.

- setup_uncertainity_analysis_tab(self): 
  Sets up the Uncertainty Analysis tab for running vehicle analyses.

- populate_input_file_information_tab(self, tab): 
  Populates the Input File Information sub-tab with configurable fields.

- populate_summary_datafields_tab(self, tab): 
  Populates the Summary Data Fields sub-tab with editable entries.

- populate_hioki_CAN_tab(self, tab): 
  Populates the Hioki CAN Analysis Field sub-tab with editable entries.

- add_save_button(self, tab): 
  Adds a save button to a given tab and centers it.

- save_configuration(self): 
  Saves the current configuration to a JSON file using UTF-8 encoding.

- submit_selection(self): 
  Gathers user input and executes the uncertainty analysis callback.

"""

import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

class GuiManager:
    def __init__(self, root,config_path selection_callback):
        """
        Initializes the GuiManager instance and sets up the main application window 
        and its tabs.

        Args:
        -----
        - root (tk.Tk): 
            The root Tkinter window object that serves as the main container 
            for the GUI.

        - config_path (str): 
            Path to the JSON configuration file used to load and save application 
            settings, including parameters for file paths, data fields, and analysis 
            configurations.
            
        - selection_callback (function): 
            A callback function executed during uncertainty analysis, triggered 
            when the "Run Uncertainty Analysis" button is clicked. It receives 
            selected vehicle, cycle, and other parameters as arguments.

        Functionality:
        --------------
        - Initializes the main GUI layout with a tabbed interface.
        - Loads the configuration data from the provided `config_path`.
        - Configures three main tabs:
            1. **Home Tab**: Displays a welcome message and application logo.
            2. **Parameter Tab**: Allows users to edit configuration parameters.
            3. **Uncertainty Analysis Tab**: Enables vehicle selection, cycle selection, 
            and running of the uncertainty analysis.

        Raises:
        -------
        - FileNotFoundError: 
            If the specified `config_path` does not exist.
        - JSONDecodeError: 
            If the configuration file contains invalid JSON.

        Example Usage:
        --------------
        >>> root = tk.Tk()
        >>> app = GuiManager(root, callback_function, "config/configuration.json")
        >>> root.mainloop()
        """

        self.config_path = config_path

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print("[ERROR] Configuration file not found. Please ensure 'configuration.json' is in the correct directory.")
            return
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse the configuration file. Ensure it is a valid JSON file.")
            return
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
        self.setup_parameter_tab() 
        self.setup_uncertainity_analysis_tab()
        
        # Pack the tab control into the main window
        self.tab_control.pack(expand=1, fill="both")
    
    def setup_home_tab(self):
        """
        Configures the Home tab in the GUI.

        Displays:
        - ANL logo.
        - Welcome message.
        - Note about following SAE J1634 Standards.
        """
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
        """
        Configures the Uncertainty Analysis tab in the GUI.

        Features:
        - Dropdown for vehicle selection.
        - Radiobuttons for selecting driving cycles.
        - Entry field for specifying the TDMS data directory.
        - Dropdown for clamp selection.
        - Button to execute uncertainty analysis.
        - Status label to display analysis results.
        """
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
        # cycle_options = ["MCT", "SMCT", "WLTC"]
        cycle_options = ["MCT"]
        for cycle in cycle_options:
            radio_button = tk.Radiobutton(
                cycle_frame, text=cycle, variable=self.selected_cycle, value=cycle,
                font=("Segoe UI", 10), bg="#e5e5f7", fg="#333", activebackground="#e5e5f7", 
                selectcolor="#a0c4ff", anchor="w"
            )
            radio_button.pack(anchor="w", padx=10)

        # # Platform Selection Label and Dropdown
        # platform_label = tk.Label(
        #     uncertainity_analysis_tab, text="Select Platform:", 
        #     font=("Segoe UI", 12), bg="#e5e5f7", fg="#333"
        # )
        # platform_label.pack(pady=(20, 5))

        # platform_options = ["Windows", "Linux"]
        # self.selected_platform = tk.StringVar()
        # platform_dropdown = ttk.Combobox(
        #     uncertainity_analysis_tab, textvariable=self.selected_platform, 
        #     font=("Segoe UI", 10), values=platform_options, state="readonly"
        # )
        # platform_dropdown.pack(pady=5)
        # platform_dropdown.set("Linux")  # Set default visible selection
        # platform_dropdown.set("Windows") 
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

    def setup_parameter_tab(self):
        """Configure the Parameter tab with three sub-tabs."""
        parameter_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(parameter_tab, text="Parameter")

        # Sub-tab control
        sub_tab_control = ttk.Notebook(parameter_tab)

        # Add sub-tabs
        input_file_tab = ttk.Frame(sub_tab_control)
        datafields_tab = ttk.Frame(sub_tab_control)
        hioki_tab = ttk.Frame(sub_tab_control)

        sub_tab_control.add(input_file_tab, text="Input-File-Information")
        sub_tab_control.add(datafields_tab, text="Summary-Data-Fields")
        sub_tab_control.add(hioki_tab, text="Hioki-CAN-Analysis-Field")

        sub_tab_control.pack(expand=1, fill="both")

        # Populate each tab with data
        self.populate_input_file_information_tab(input_file_tab)
        self.add_save_button(input_file_tab)

        self.populate_summary_datafields_tab(datafields_tab)
        self.add_save_button(datafields_tab)

        self.populate_hioki_CAN_tab(hioki_tab)
        self.add_save_button(hioki_tab)

        # Add a status label for save success message
        self.status_label = tk.Label(parameter_tab, text="", font=("Segoe UI", 12), fg="green", bg="#e5e5f7")
        self.status_label.pack(pady=20, anchor="center")

    def populate_input_file_information_tab(self, tab):
        """Populate the Input File Information sub-tab with fields from the configuration."""
        label = tk.Label(tab, text="Input File Information", font=("Segoe UI", 12), bg="#007bff", fg="white", padx=10, pady=5)
        label.pack(fill="x")
        
        fields = ["InputFileName", "InputSheetName", "NoOfSkipRows", "MaxSubPhase"]
        self.input_file_entries = {}

        row_colors = ["#f9f9f9", "#e9ecef"]  # Alternating row colors

        for idx, field in enumerate(fields):
            row_color = row_colors[idx % 2]  # Alternate row color
            frame = tk.Frame(tab, bg=row_color)
            frame.pack(fill="x", pady=2, padx=5)

            label = tk.Label(frame, text=field, font=("Segoe UI", 12), bg=row_color)
            label.pack(side="left", padx=5)

            entry = tk.Entry(frame, font=("Segoe UI", 10))
            entry.insert(0, str(self.config.get(field, "")))
            entry.pack(side="left", fill="x", expand=True, padx=5)

            self.input_file_entries[field] = entry

    def populate_summary_datafields_tab(self, tab):
        """Populate the Sumary Data Fields sub-tab with editable entries."""
        label = tk.Label(tab, text="Summary DataFields", font=("Segoe UI", 12), bg="#007bff", fg="white", padx=10, pady=5)
        label.pack(fill="x")

        self.datafields_entries = {}
        datafields = self.config.get("DataFields", {})

        row_colors = ["#f9f9f9", "#e9ecef"]  # Alternating row colors

        for idx, (key, value) in enumerate(datafields.items()):
            row_color = row_colors[idx % 2]  # Alternate row color
            frame = tk.Frame(tab, bg=row_color)
            frame.pack(fill="x", pady=2, padx=5)

            label = tk.Label(frame, text=key, font=("Segoe UI", 12), bg=row_color)
            label.pack(side="left", padx=5)

            entry = tk.Entry(frame, font=("Segoe UI", 10))
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True, padx=5)

            self.datafields_entries[key] = entry

    def populate_hioki_CAN_tab(self, tab):
        """Populate the Hioki-CAN-Analysis-Field sub-tab."""
        label = tk.Label(tab, text="Hioki-CAN-Analysis-Field", font=("Segoe UI", 12), bg="#007bff", fg="white", padx=10, pady=5)
        label.pack(fill="x")

        self.hioki_entries = {}
        hioki_data = self.config.get("Hioki-CAN-Analysis-Field", {})

        row_colors = ["#f9f9f9", "#e9ecef"]  # Alternating row colors

        for idx, (key, value) in enumerate(hioki_data.items()):
            row_color = row_colors[idx % 2]  # Alternate row color
            frame = tk.Frame(tab, bg=row_color)
            frame.pack(fill="x", pady=2, padx=5)

            label = tk.Label(frame, text=key, font=("Segoe UI", 12), bg=row_color)
            label.pack(side="left", padx=5)

            entry = tk.Entry(frame, font=("Segoe UI", 10))
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True, padx=5)

            self.hioki_entries[key] = entry
   
    def add_save_button(self, tab):
        """Add a Save button to a given tab and center it."""
        save_button = tk.Button(
            tab, text="Save", font=("Segoe UI", 10, "bold"),
            bg="#1a73e8", fg="#fff", activebackground="#0066cc", activeforeground="#fff",
            relief="flat", command=self.save_configuration
        )
        save_button.pack(pady=20, anchor="center")

    def save_configuration(self):
        """Save the updated fields to the configuration file."""
        try:
            # Update the configuration with the current entries
            for field, entry in self.input_file_entries.items():
                self.config[field] = entry.get()

            datafields = {}
            for key, entry in self.datafields_entries.items():
                datafields[key] = entry.get()
            self.config["DataFields"] = datafields

            hioki_data = {}
            for key, entry in self.hioki_entries.items():
                hioki_data[key] = entry.get()
            self.config["Hioki-CAN-Analysis-Field"] = hioki_data

            # Write the updated configuration to the file
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)

            # Update the status label in the GUI
            if hasattr(self, 'status_label'):
                self.status_label.config(
                    text="Your changes have been saved to the configuration file.",
                    fg="green", font=("Segoe UI", 12, "bold")
                )
                self.status_label.pack(anchor="center")
        except Exception as e:
            # Handle any errors during save
            if hasattr(self, 'status_label'):
                self.status_label.config(
                    text=f"Error saving configuration: {e}",
                    fg="red", font=("Segoe UI", 12, "bold")
                )
                self.status_label.pack(anchor="center")



        # Show success message
        # messagebox.showinfo("Configuration Saved", "Your changes have been saved to the configuration file.")

    def submit_selection(self):
        """
        Gathers user selections from the GUI and executes the analysis via the callback function.

        Inputs:
        - Vehicle selection.
        - Driving cycle selection.
        - TDMS data directory.
        - Clamp selection.

        Provides:
        - Success or failure feedback in the status label.
        - Prints error message in case of failure.
        """
        # Get selected values
        selected_vehicle = self.selected_vehicle.get()
        selected_cycle = self.selected_cycle.get()
        # selected_platform = self.selected_platform.get()
        tdms_data_directory = self.data_directory.get()
        selected_clamp = self.selected_clamp.get()
        
        # Perform analysis with selected values
        try:
            self.selection_callback(selected_vehicle, selected_cycle, tdms_data_directory, selected_clamp)
            self.status_label.config(text="Successfully Completed Uncertainty Analysis!", fg="green", font=("Segoe UI", 14, "bold"))
        except Exception as e:
            self.status_label.config(text="Uncertainty Analysis Failed!", fg="red", font=("Segoe UI", 14, "bold"))
            print("Error during analysis:", e)
    
    def __del__(self):
        """
        Cleans up resources upon object destruction.
        """
        object_name = "GuiManager object"
        print(f"{object_name} is destroyed.")

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
    app = GuiManager(root, config_path="config-files/configuration.json", selection_callback=test_callback)
    root.mainloop()
