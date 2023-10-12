/*
**********************************************************************************

**********************************************************************************
  VehicleStatus.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is a data structure declaration for vehicle-status-manager class.
*/

#pragma once
#include "string"

struct VehicleStatus
{
    int vehicleID;
    int activeIntersectionId;
    int vehicleSignalGroup;
    double vehicleLatitude;
    double vehicleLongitude;
    double vehicleElevation;
    double vehicleHeading;
    double vehicleSpeed;
    

    void reset()
    {
        vehicleID = 0;
        activeIntersectionId;
        vehicleSignalGroup = 0;
        vehicleLatitude = 0.0;
        vehicleLongitude = 0.0;
        vehicleElevation = 0.0;
        vehicleHeading = 0.0;
        vehicleSpeed = 0.0;
    }
};