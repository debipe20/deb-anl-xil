/*
**********************************************************************************

**********************************************************************************
  VehicleStatusManger.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is the demonstration of VehicleStatusManger API.
*/
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

    MapManager mapManager;
    BasicVehicle basicVehicle;
    BsmManager bsmManager;

    const string HostIP = jsonObject["HostIp"].asString();
    UdpSocket mapManagerSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["MapManager"].asInt()));
    
    char receiveBuffer[2048];
    int msgType{};

    while (true)
    {
        mapManagerSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedJsonString(receiveBuffer);
        msgType = mapManager.getMessageType(receivedJsonString);

        if (msgType == MsgEnum::DSRCmsgID_bsm)
        {
            basicVehicle.json2BasicVehicle(receivedJsonString);
            bsmManager.getVehicleInformationFromMAP(mapManager, basicVehicle);
            cout<<"Signal group is " << bsmManager.getSignalGroup() << endl;;
        }

        else if (msgType == MsgEnum::DSRCmsgID_map)
        {
            mapManager.json2MapPayload(receivedJsonString);
            mapManager.maintainAvailableMapList();
            mapManager.updateMapAge();
            mapManager.deleteMapPayLoadFromList();
        }
    }

    mapManagerSocket.closeSocket();
    return 0;
}