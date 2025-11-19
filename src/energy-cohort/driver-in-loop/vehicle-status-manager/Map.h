/*
**********************************************************************************

Map.h
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
Revision History:
  1. This script is contains the data structure for MapManager


**********************************************************************************
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
        int minuteOfYear;
        int secondOfMinute;
        std::string activeMapStatus;
        void reset() 
        {
            availableMapPayload = "";
            availableMapFileName = "";
            availableMapFileDirectory = "";
            mapIntersectionID = 0;
            mapAge = 0; 
            minuteOfYear = 0;
            secondOfMinute = 0;
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