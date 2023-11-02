/*
**********************************************************************************

**********************************************************************************
  bsm-generator-main.cpp
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is the demonstration of BsmGenerator API.
*/
#include "BsmGenerator.h"
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

    const string HostIP = jsonObject["HostIp"].asString();
    UdpSocket bsmGeneratorSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["BsmGenerator"].asInt()));
    // const int msgReceiverPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["MessageReceiver"].asInt());
    const int dataConverterPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["DataConverter"].asInt());

    string bsmLogFile = jsonObject["BsmLogFileName"].asString();
    char receiveBuffer[2048];
    int msgType{};
    string sendingString{};

    BsmGenerator bsmGenerator(bsmLogFile);

    while (true)
    {
        bsmGeneratorSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedJsonString(receiveBuffer);

        msgType = bsmGenerator.getMessageType(receivedJsonString);
        
        if (msgType == static_cast<int>(msgType::speedData))
        {
          sendingString = bsmGenerator.BsmEncoder(receivedJsonString);
          // bsmGeneratorSocket.sendData(HostIP, static_cast<short unsigned int>(msgReceiverPort), sendingString);
          bsmGeneratorSocket.sendData(HostIP, static_cast<short unsigned int>(dataConverterPort), sendingString);
        }
    }

    return 0;
}