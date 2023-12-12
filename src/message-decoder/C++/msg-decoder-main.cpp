#include "MsgDecoder.h"
#include <UdpSocket.h>
#include "geoUtils.h"
#include "msgEnum.h"
#include <algorithm>
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

    MsgDecoder msgDecoder;
    const string HostIP = jsonObject["HostIp"].asString();
    UdpSocket msgDecoderSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["MessageDecoder"].asInt()));
    const int spatManagerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["SpatManager"].asInt());
    
    char receiveBuffer[2048];
    // string receivedPayload{};
    // string extractedPayload{};
    int msgType{};
    string sendingJsonString{};

    while (true)
    {
        msgDecoderSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedPayload(receiveBuffer);
        cout << receivedPayload << endl;
        size_t pos = receivedPayload.find("001");
        cout << pos << endl;
        receivedPayload = receivedPayload.erase(0,pos);
        
        msgType = msgDecoder.getMessageType(receivedPayload);

            if (msgType == MsgEnum::DSRCmsgID_map)
            {
                cout << "Received MAP" <<endl;
            }

            else if (msgType == MsgEnum::DSRCmsgID_bsm)
            {
                cout << "Received BSM" <<endl;
            }

            else if (msgType == MsgEnum::DSRCmsgID_spat)
            {
                cout << "Received SPaT" <<endl;
                sendingJsonString = msgDecoder.spatDecoder(receivedPayload);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(spatManagerPort), sendingJsonString);
            }

        // receivedPayload = msgDecoderSocket.receivePayloadHexString();
        // cout << receivedPayload << endl;
        // size_t pos = receivedPayload.find("001");

        // if (pos != string::npos)
        // {
        //     extractedPayload = receivedPayload.erase(0, pos);
        //     msgType = msgDecoder.getMessageType(extractedPayload);

        //     if (msgType == MsgEnum::DSRCmsgID_map)
        //     {

        //     }

        //     else if (msgType == MsgEnum::DSRCmsgID_bsm)
        //     {

        //     }

        //     else if (msgType == MsgEnum::DSRCmsgID_spat)
        //     {

        //     }
        // }
    }
    
    return 0;
}