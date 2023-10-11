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

	if (parsingSuccessful == true)
	{
		if ((jsonObject["MsgType"]).asString() == "MAP")
			messageType = MsgEnum::DSRCmsgID_map;

		else if ((jsonObject["MsgType"]).asString() == "BSM")
			messageType = MsgEnum::DSRCmsgID_bsm;

        else if ((jsonObject["MsgType"]).asString() == "SignalGroupDataMessage")
			messageType = static_cast<int>(msgType::signalStatusData);
	}

	return messageType;
}

/*
    - Check if it is required to send signal group data request message or not
*/
bool VehicleStatusManager::checkSignalGroupDataRequestSendingStatus()
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


VehicleStatusManager::~VehicleStatusManager()
{
}