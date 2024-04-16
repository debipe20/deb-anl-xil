"""
**********************************************************************************

data-post-processing.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
  1. This script contains methodology to generate csv files that can be fed to the Autonomie.
"""

import json 
from DataManager import DataManager

def main():
    # Read the config file into a json object:
    configFile = open("configuration-solo-run.json", 'r')
    config = (json.load(configFile))
    # Close the config file:
    configFile.close()

    dataManager = DataManager(config)
    dataManager.processRawData()
    

if __name__ == "__main__":
    main()