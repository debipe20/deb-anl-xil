/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManager.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is header file for VehicleStatusManager.cpp
*/

#pragma once
#include "VehicleStatus.h"
#include "MapManager.h"
#include "BsmManager.h"

#define SignalGroupData_Time_Gap_Value 0.25

enum msgType
{
    signalGroupData = 1,
};

class VehicleStatusManager
{
private:
    // int currentSignalStatus{};
    double signalGroupDataRequestSendingTime{0.0};
    vector<VehicleStatus>vehicleStatusList{};

public:
    VehicleStatusManager();
    ~VehicleStatusManager();

    int getMessageType(string jsonString);
    void manageVehicleStatusList(BasicVehicle basicVehicle);
    void updateVehicleStatusList(BsmManager bsmManager);
    void manageSignalGroupData(string jsonString);
    bool checkSignalGroupDataRequestSendingStatus();
    // bool checkCurrentSignalStatusDataSendingRequirement();
    string getSignalGroupDataRequestJsonString(BsmManager bsmManager);
    string getCurrentSignalStatusDataJsonString();
};
