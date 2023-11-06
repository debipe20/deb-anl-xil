/*
**********************************************************************************

**********************************************************************************
  Map.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is a data structure declaration for map-manager class.
*/

#pragma once
#include "string"

namespace Map
{
    struct AvailableMap
    {
        std::string availableMapPayload;
        std::string availableMapFileName;
        std::string availableMapFileDirectory;
        int mapIntersectionID;
        double mapAge;
        double mapReceivingTime;

        std::string activeMapStatus;

        void reset() 
        {
            availableMapPayload = "";
            availableMapFileName = "";
            availableMapFileDirectory = "";
            mapIntersectionID = 0;
            mapAge = 0; 
            mapReceivingTime = 0.0;
            activeMapStatus = "False";
        }
        
    };
    struct ActiveMap
    {
        std::string activeMapFileName;
        std::string activeMapFileDirectory;
        void reset()
        {
            activeMapFileName = "";
            activeMapFileDirectory = "";
        }

    };
}; 