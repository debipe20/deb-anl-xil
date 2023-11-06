/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManager.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is main class for VehicleStatusManager. It contains definition of the methods.
*/

#include "VehicleStatusManager.h"

VehicleStatusManager::VehicleStatusManager()
{
    signalGroupDataRequestSendingTime = getPosixTimestamp();
}

/*
    -Get the message type based on the received json string
*/
int VehicleStatusManager::getMessageType(string jsonString)
{
    int messageType{};
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};

    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
    delete reader;

    if (parsingSuccessful)
    {
        if ((jsonObject["MsgType"]).asString() == "MAP")
            messageType = MsgEnum::DSRCmsgID_map;

        else if ((jsonObject["MsgType"]).asString() == "BSM")
            messageType = MsgEnum::DSRCmsgID_bsm;

        else if ((jsonObject["MsgType"]).asString() == "SignalGroupDataMessage")
            messageType = static_cast<int>(msgType::signalGroupData);
    }

    return messageType;
}

/*
    - Method to create vehicle status list based on BSM
*/
void VehicleStatusManager::manageVehicleStatusList(BasicVehicle basicVehicle)
{
    VehicleStatus vehicleStatus;
    vehicleStatus.reset();
    vehicleStatusList.clear();

    vehicleStatus.vehicleID = basicVehicle.getTemporaryID();
    vehicleStatus.vehicleLatitude = basicVehicle.getLatitude_DecimalDegree();
    vehicleStatus.vehicleLongitude = basicVehicle.getLongitude_DecimalDegree();
    vehicleStatus.vehicleElevation = basicVehicle.getElevation_Meter();
    vehicleStatus.vehicleHeading = basicVehicle.getHeading_Degree();
    vehicleStatus.vehicleSpeed = basicVehicle.getSpeed_MeterPerSecond();

    vehicleStatusList.push_back(vehicleStatus);
}

/*
    - Method to update active Map's intersection id and signal group infomation along vehicle travel direction 
*/
void VehicleStatusManager::updateVehicleStatusList(BsmManager bsmManager)
{
    vehicleStatusList.at(0).vehicleSignalGroup = bsmManager.getVehicleSignalGroup();
    vehicleStatusList.at(0).vehicleDistanceFromStopBar = bsmManager.getVehicleDistanceFromStopBar();
    vehicleStatusList.at(0).activeIntersectionId = bsmManager.getVehicleIntersectionId(); 
}

/*
    - Check if it is required to send signal group data request message or not
*/
bool VehicleStatusManager::checkSignalGroupDataRequestSendingStatus()
{
    bool signalGroupDataRequestSendingStatus{false};
    double currentTime = getPosixTimestamp();

    if (vehicleStatusList.at(0).vehicleSignalGroup != 0 && (currentTime - signalGroupDataRequestSendingTime) >= SignalGroupData_Time_Gap_Value)
    {
        signalGroupDataRequestSendingStatus = true;
        signalGroupDataRequestSendingTime = currentTime;
    }

    return signalGroupDataRequestSendingStatus;
}

string VehicleStatusManager::getSignalGroupDataRequestJsonString(BsmManager bsmManager)
{
    string signalGroupDataRequestJsonString{};

    Json::Value jsonObject;
    Json::StreamWriterBuilder builder;
    builder["commentStyle"] = "None";
    builder["indentation"] = "";

    jsonObject["MsgType"] = "SignalGroupDataRequest";
    jsonObject["IntersectionId"] = bsmManager.getVehicleIntersectionId();
    jsonObject["SignalGroup"] = bsmManager.getVehicleSignalGroup();
    
    signalGroupDataRequestJsonString = Json::writeString(builder, jsonObject);

    return signalGroupDataRequestJsonString;
}

void VehicleStatusManager::manageSignalGroupData(string jsonString)
{
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};

    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
    delete reader;

    if (parsingSuccessful && jsonObject["DataAvalability"])
        vehicleStatusList.at(0).vehicleSignalGroupState = jsonObject["EventState"].asInt();

    else if (parsingSuccessful && !jsonObject["DataAvalability"])
        vehicleStatusList.at(0).vehicleSignalGroupState = 0;
}

// bool VehicleStatusManager::checkCurrentSignalStatusDataSendingRequirement()
// {
//     bool currentSignalStatusDataSendingRequirement{false};

//     if (currentSignalStatus != vehicleStatusList.at(0).vehicleSignalGroupState)
//         currentSignalStatusDataSendingRequirement = true;

//     return currentSignalStatusDataSendingRequirement;
// }

string VehicleStatusManager::getCurrentSignalStatusDataJsonString()
{
    string currentSignalStatusDataJsonString{};

    Json::Value jsonObject;
    Json::StreamWriterBuilder builder;
    builder["commentStyle"] = "None";
    builder["indentation"] = "";

    jsonObject["MsgType"] = "CurrentSignalStatusData";
    jsonObject["SignalGroup"] = vehicleStatusList.at(0).vehicleSignalGroup;
    jsonObject["EventState"] = vehicleStatusList.at(0).vehicleSignalGroupState;
    jsonObject["DistanceFromStopBar"] = vehicleStatusList.at(0).vehicleDistanceFromStopBar;

    currentSignalStatusDataJsonString = Json::writeString(builder, jsonObject);

    return currentSignalStatusDataJsonString;
}

VehicleStatusManager::~VehicleStatusManager()
{
}