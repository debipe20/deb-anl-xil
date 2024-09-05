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

import json
from TestIDManager import TestIDManager
from TdmsFileManager import TdmsFileManager

def main():
    
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    test_id_manager = TestIDManager(config)
    tdms_file_manager = TdmsFileManager(config)    
    test_id_manager.manage_test_id()
    tdms_file_manager.get_tdm_file_path()

if __name__ == "__main__":
    main()  