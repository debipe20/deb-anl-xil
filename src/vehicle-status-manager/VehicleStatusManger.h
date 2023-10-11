/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManger.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is header file for VehicleStatusManger.cpp
*/

#pragma once
#include "MapManager.h"
#include "BsmManager.h"

#define SignalGroupData_Time_Gap_Value 2.0

class VehicleStatusManger
{
private:
    double signalGroupDataRequestSendingTime{0.0};

public:
    VehicleStatusManger();
    ~VehicleStatusManger();

    bool checkSignalGroupDataRequestSendingStatus();
    string getSignalGroupDataRequestJsonString();
};
