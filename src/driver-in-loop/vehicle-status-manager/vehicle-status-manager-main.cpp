/*
**********************************************************************************

vehicle-status-manager-main.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
This script:


**********************************************************************************
*/

#include "VehicleStatusManager.h"
#include <UdpSocket.h>
#include <cstdlib> 

int main()
{
    string homeDir = getenv("HOME");  // Works on Linux
    string configFilePath = homeDir + "/Desktop/deb-anl-xil/config/anl-master-config.json";

    cout << "Config file path: " << configFilePath << endl;   

    Json::Value jsonObject;
    // ifstream configJson("/nojournal/bin/mmitss-phase3-master-config.json");
    ifstream configJson(configFilePath);
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader * reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);        
    delete reader;

    VehicleStatusManager vehicleStatusManager;
    MapManager mapManager;
    SpatManager spatManager;
    BasicVehicle basicVehicle;
    
    UdpSocket vehicleStatusManagerSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleStatusManager"].asInt()));
    const string driverInLoopTestManagerIP = jsonObject["IPAddress"]["HostIp"].asString();
    const int driverInLoopTestManagerPortNo = static_cast<short unsigned int>(jsonObject["PortNumber"]["DriverInLoopTestManager"].asInt());
    
    cout << "Successfully open Socket" << endl;
    
    char receiveBuffer[40960];
    int msgType{};
    string sendingJsonString{};

    while (true)
    {
        vehicleStatusManagerSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedJsonString(receiveBuffer);
        msgType = vehicleStatusManager.getMessageType(receivedJsonString);

        if (msgType == MsgEnum::DSRCmsgID_bsm)
        {
            basicVehicle.json2BasicVehicle(receivedJsonString);
            cout << "Received Basic Vehicle Data\n" << receivedJsonString << endl;
            vehicleStatusManager.getVehicleInformationFromMAP(mapManager, basicVehicle);            
            sendingJsonString = vehicleStatusManager.createJsonStringForDriverInLoopTestManager();
            vehicleStatusManagerSocket.sendData(driverInLoopTestManagerIP, static_cast<short unsigned int>(driverInLoopTestManagerPortNo), sendingJsonString);
            // Update the Map status (MapAge, or delete old Map)
            vehicleStatusManager.manageMapStatusInAvailableMapList(mapManager);      
        }

        else if (msgType == MsgEnum::DSRCmsgID_map)
        {
            mapManager.json2MapPayload(receivedJsonString);
            mapManager.maintainAvailableMapList();
            mapManager.printAvailableMapList();
        }

        else if (msgType == MsgEnum::DSRCmsgID_spat)
        {
            spatManager.delete_timed_out_spat_data_from_available_spat_list();
        }
        

        else if (msgType == static_cast<int>(msgType::carlaTrafficLightStatus))
        {
            vehicleStatusManager.setTrafficSignalState(receivedJsonString);
        }
    }
    
    vehicleStatusManagerSocket.closeSocket();
    return 0;
}