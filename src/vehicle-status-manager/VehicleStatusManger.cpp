/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManger.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is main class for VehicleStatusManger. It contains definition of the methods.
*/

#include "VehicleStatusManger.h"

VehicleStatusManger::VehicleStatusManger()
{
    signalGroupDataRequestSendingTime = getPosixTimestamp();
}

/*
    - Check if it is required to send signal group data request message or not
*/
bool VehicleStatusManger::checkSignalGroupDataRequestSendingStatus()
{
    bool signalGroupDataRequestSendingStatus{false};
    double currentTime = getPosixTimestamp();

    if ((currentTime - signalGroupDataRequestSendingTime) >= SignalGroupData_Time_Gap_Value)
    {
        signalGroupDataRequestSendingStatus = true;
        signalGroupDataRequestSendingTime = currentTime;
    }

    return signalGroupDataRequestSendingStatus;
}

string VehicleStatusManger::getSignalGroupDataRequestJsonString()
{

}


VehicleStatusManger::~VehicleStatusManger()
{
}