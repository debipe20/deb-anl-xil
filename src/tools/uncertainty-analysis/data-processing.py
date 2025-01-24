"""
**********************************************************************************

data-processing.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
This script serves as an API for data processing and uncertainty analysis using 
the GUI-based selection interface. It integrates the following key functionalities:
1. Provides a GUI for user input using the `GuiManager` class.
2. Processes selected inputs to manage test data using the `TestIdManager` class.
3. Executes uncertainty analysis based on user-provided parameters.

Classes:
--------
- `GuiManager`: Handles the graphical user interface (GUI) for selecting vehicles, 
  driving cycles, data directories, and clamps. It allows the user to trigger 
  analysis tasks with a button click.
- `TestIdManager`: Manages test data processing, including filtering, categorization, 
  and analysis of driving cycle data based on selected parameters.

Functions:
----------
- `main()`: 
    - Reads configuration settings from a JSON file.
    - Initializes the Tkinter GUI using `GuiManager`.
    - Defines the callback function `on_selections_made` to process user inputs 
      and trigger uncertainty analysis via `TestIdManager`.

Usage:
------
Run this script to launch the GUI for managing and analyzing uncertainty data. 
Once selections are made in the GUI, the application processes the data 
according to the specified configurations and saves the results.

Example:
--------
To start the application, simply run:
    $ python data-processing.py

"""

import tkinter as tk
from TestIdManager import TestIdManager
from GuiManager import GuiManager

def main():
    """
    Main entry point of the application.

    Responsibilities:
    ------------------
    - Initializes the Tkinter GUI using the `GuiManager` class.
    - Defines the callback function `on_selections_made` to handle user input and
      trigger uncertainty analysis via the `TestIdManager` class.

    Workflow:
    ---------
    1. Launches the GUI for user interaction, where users select:
       - Vehicle type.
       - Driving cycle.
       - Data directory (TDMS files).
       - Instrument clamp.
    2. On user input, the `on_selections_made` callback processes the data and
       executes the uncertainty analysis.

    Returns:
    --------
    None
    """
    config_path = "config-files/configuration.json"
    root = tk.Tk()

    # Define callback function to process selections
    def on_selections_made(selected_vehicle, selected_cycle, tdms_data_directory, selected_clamp):
        """
        Callback function to process user selections and execute uncertainty analysis.

        Parameters:
        -----------
        selected_vehicle : str
            The vehicle type selected by the user (e.g., "2020 Tesla Model 3").
        selected_cycle : str
            The driving cycle selected by the user (e.g., "MCT").
        tdms_data_directory : str
            The directory containing the TDMS test data files.
        selected_clamp : str
            The instrument clamp selected by the user for the analysis (e.g., "CT6843-05").

        Workflow:
        ---------
        1. Displays the user's selections in the console for verification.
        2. Initializes the `TestIdManager` class with the selected parameters.
        3. Calls the `manage_test_data()` method of `TestIdManager` to process the test data
           and perform the uncertainty analysis.

        Exceptions:
        -----------
        Any exceptions raised during the analysis process will terminate the execution
        and must be logged or handled appropriately.

        Returns:
        --------
        None
        """
        print("\n[INFO] Executing Uncertainty Analysis with the following parameters:")
        print(f"  - Selected Vehicle       : {selected_vehicle}")
        print(f"  - Selected Driving Cycle : {selected_cycle}")
        print(f"  - Data Directory         : {tdms_data_directory}")
        print(f"  - Instrument Clamp       : {selected_clamp}")
        
        try:
            test_id_manager = TestIdManager(selected_vehicle, selected_cycle, tdms_data_directory, selected_clamp)
            test_id_manager.manage_test_data()
            del test_id_manager
            print("\n[INFO] Uncertainty Analysis completed successfully.")
        except Exception as e:
            print("\n[ERROR] An error occurred during the Uncertainty Analysis.")
            print(f"  - Error Details: {e}")
            
    gui_manager = GuiManager(root, config_path, selection_callback = on_selections_made)
    root.mainloop()
    root.destroy()
    del gui_manager

if __name__ == "__main__":
    main()
