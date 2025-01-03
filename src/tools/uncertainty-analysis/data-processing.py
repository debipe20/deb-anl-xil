"""
**********************************************************************************

data-processing.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods is an API for data mining:
********
"""
import tkinter as tk
import json
from TestIDManager import TestIDManager
from GuiManager import GuiManager

def main():
    
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    root = tk.Tk()

    # Define callback function to process selections
    def on_selections_made(selected_vehicle, selected_cycle, selected_platform, tdms_data_directory, selected_clamp):
        print("Selected Vehicle: ", selected_vehicle)
        print("Selected Driving Cycle: ", selected_cycle)
        print("Selected Platform: ", selected_platform)
        print("Selected Data Directory: ", tdms_data_directory)
        print("Selected Clamp: ", selected_clamp)
        test_id_manager = TestIDManager(selected_vehicle, selected_cycle, selected_platform, tdms_data_directory, selected_clamp)
        test_id_manager.manage_test_data()

        print("Completed Uncertainity Analysis!")
    gui_manager = GuiManager(root, selection_callback=on_selections_made)
    root.mainloop()


if __name__ == "__main__":
    main()  