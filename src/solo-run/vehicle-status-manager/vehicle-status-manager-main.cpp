/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManager.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is the demonstration of VehicleStatusManager API.
*/
#include "VehicleStatusManager.h"
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

    BasicVehicle basicVehicle;
    MapManager mapManager;
    BsmManager bsmManager;
    VehicleStatusManager vehicleStatusManager;

    const string HostIP = jsonObject["IPAddress"]["HostIp"].asString();
    UdpSocket vehicleStatusManagerSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleStatusManager"].asInt()));
    const int spatManagerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["SpatManager"].asInt());
    const int bsmGeneratorPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["BsmGenerator"].asInt());
    const int leadVehicleDataGeneratorPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["LeadVehicleDataManager"].asInt());
    char receiveBuffer[2048];
    int msgType{};
    string sendingJsonString{};
    string sendingHexString{};

    while (true)
    {
        vehicleStatusManagerSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedJsonString(receiveBuffer);
        msgType = vehicleStatusManager.getMessageType(receivedJsonString);


        if (msgType == MsgEnum::DSRCmsgID_bsm)
        {   
            // cout<<"Received Bsm is " << receivedJsonString << endl;;
            basicVehicle.json2BasicVehicle(receivedJsonString);
            bsmManager.getVehicleInformationFromMAP(mapManager, basicVehicle);
            vehicleStatusManager.manageVehicleStatusList(basicVehicle);
            vehicleStatusManager.updateVehicleStatusList(bsmManager);
            // cout<<"**************Signal group is " << bsmManager.getVehicleSignalGroup() << " **************" <<endl;;
            sendingHexString = vehicleStatusManager.getEncodedHexData();
            cout << "Encoded hexadecimal representation: " << sendingHexString << endl;
            vehicleStatusManagerSocket.sendData(HostIP, static_cast<short unsigned int>(leadVehicleDataGeneratorPort), sendingHexString);

            if (vehicleStatusManager.checkSignalGroupDataRequestSendingStatus())
            {
                sendingJsonString = vehicleStatusManager.getSignalGroupDataRequestJsonString(bsmManager);
                vehicleStatusManagerSocket.sendData(HostIP, static_cast<short unsigned int>(spatManagerPort), sendingJsonString);
                // cout << "Send Signal Group Data Request message" << endl;
            }
        }

        else if (msgType == MsgEnum::DSRCmsgID_map)
        {
            mapManager.json2MapPayload(receivedJsonString);
            mapManager.maintainAvailableMapList();
            mapManager.updateMapAge();
            mapManager.deleteMapPayLoadFromList();
        }


        else if (msgType == static_cast<int>(msgType::signalGroupData))
        {
            vehicleStatusManager.manageSignalGroupData(receivedJsonString);
            sendingJsonString = vehicleStatusManager.getCurrentSignalStatusDataJsonString();
            vehicleStatusManagerSocket.sendData(HostIP, static_cast<short unsigned int>(bsmGeneratorPort), sendingJsonString);
            // cout << "Received Signal Group Data from Spat Manager" << endl;
            // cout << "Send Following Signal Group Data to Bsm Generator\n" << sendingJsonString << endl;
        }
    }

    vehicleStatusManagerSocket.closeSocket();
    return 0;
}