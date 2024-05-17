/*
**********************************************************************************

**********************************************************************************
  lvdm-main.cpp
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is the demonstration of LeadVehicleDataManager API.
*/
#include "LeadVehicleDataManager.h"
#include <UdpSocket.h>

int main()
{
    Json::Value jsonObject;
    std::ifstream configJson("/nojournal/bin/anl-master-config.json");
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader * reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);        
    delete reader;

    const string HostIP = jsonObject["IPAddress"]["HostIp"].asString();
    UdpSocket leadVehicleDataManagerSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["LeadVehicleDataManager"].asInt()));
    const int vehicleControllerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleController"].asInt());

    char receiveBuffer[2048];
    int msgType{};
    string sendingString{};
    string receivedPayload{};
    string extractedPayload{};

    LeadVehicleDataManager leadVehicleDataManager;

    while (true)
    {
        receivedPayload = leadVehicleDataManagerSocket.receivePayloadHexString();
        cout << "Received Payload is: \n" << receivedPayload << endl;
        size_t pos = receivedPayload.find("001");
        extractedPayload = receivedPayload.erase(0, pos);
        
        msgType = leadVehicleDataManager.getMessageType(extractedPayload);
        cout << "Received message type is: " << msgType << endl;

        if (msgType == MsgEnum::DSRCmsgID_bsm)
        {
            string bsmJsonString = leadVehicleDataManager.bsmDecoder(extractedPayload);
            cout << "Decoded BSM is: \n" << bsmJsonString << endl;
        }

          
    }

    return 0;
}