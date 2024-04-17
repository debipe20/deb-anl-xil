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
from PlotManager import PlotManager

def main():

    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()

    plotManager = PlotManager(config)
    plotManager.plotSpeedProfile()

if __name__ == "__main__":
    main()  