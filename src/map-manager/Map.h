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