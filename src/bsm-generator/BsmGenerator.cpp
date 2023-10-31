/*
**********************************************************************************

**********************************************************************************
  BsmGenerator.cpp
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is main class for BsmGenerator. It contains definition of the methods.
*/

#include "BsmGenerator.h"

// using namespace GeoUtils;
// using namespace MsgEnum;

BsmGenerator::BsmGenerator(string logfile)
{
    // Json::Value jsonObject;
	// Json::CharReaderBuilder builder;
	// Json::CharReader *reader = builder.newCharReader();
	// string errors{};
	// ifstream jsonconfigfile("/nojournal/bin/anl-master-config.json");

	// string configJsonString((std::istreambuf_iterator<char>(jsonconfigfile)), std::istreambuf_iterator<char>());
	// reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);
	// delete reader;
    
    inputFile.open(logfile, ios::in);
}

/*
    -Get the message type based on the received json string
*/
int BsmGenerator::getMessageType(string jsonString)
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
        if ((jsonObject["MsgType"]).asString() == "SpeedData")
            messageType = static_cast<int>(msgType::speedData);
    }

    return messageType;
}

void BsmGenerator::readPreloadedCoordinates()
{
    string line{};

   while(getline(inputFile, line))
}

void BsmGenerator::getNearestGpsCoordinates()
{

}

// string BsmGenerator::BsmEncoder(string jsonString)
// {
//     BasicVehicle basicVehicle;
//     stringstream payloadstream{};
//     string bsmMessagePayload;
//     /// buffer to hold message payload
//     size_t bufSize = DsrcConstants::maxMsgSize;
//     vector<uint8_t> buf(bufSize, 0);
//     basicVehicle.json2BasicVehicle(jsonString);
//     /// dsrcFrameIn to store input to UPER encoding function
//     Frame_element_t dsrcFrameIn;
//     dsrcFrameIn.reset();

//     /// manual input bsmIn
//     dsrcFrameIn.dsrcMsgId = MsgEnum::DSRCmsgID_bsm;
//     BSM_element_t &bsmIn = dsrcFrameIn.bsm;
//     bsmIn.msgCnt = 1;
//     bsmIn.id = basicVehicle.getTemporaryID();
//     bsmIn.timeStampSec = static_cast<int16_t>(basicVehicle.getSecMark_Second());
//     bsmIn.latitude = DsrcConstants::unit2damega<int32_t>(basicVehicle.getLatitude_DecimalDegree());
//     bsmIn.longitude = DsrcConstants::unit2damega<int32_t>(basicVehicle.getLongitude_DecimalDegree());
//     bsmIn.elevation = DsrcConstants::unit2deca<int32_t>(basicVehicle.getElevation_Meter());
//     bsmIn.yawRate = 0;
//     bsmIn.vehLen = 1200;
//     bsmIn.vehWidth = 300;
//     bsmIn.speed = DsrcConstants::kph2unit<uint16_t>(basicVehicle.getSpeed_MeterPerSecond() * MPS_TO_KPH_CONVERSION);
//     bsmIn.heading = DsrcConstants::heading2unit<uint16_t>(basicVehicle.getHeading_Degree());

//     /// encode BSM payload
//     size_t payload_size = AsnJ2735Lib::encode_msgFrame(dsrcFrameIn, &buf[0], bufSize);
//     if (payload_size > 0)
//     {
//         for (size_t i = 0; i < payload_size; i++)
//             payloadstream << std::uppercase << std::setw(2) << std::setfill('0') << std::hex << static_cast<unsigned int>(buf[i]);
//     }

//     bsmMessagePayload = payloadstream.str();
//     bsmMsgCount = bsmMsgCount + 1;

//     return bsmMessagePayload;
// }


BsmGenerator::~BsmGenerator()
{
    inputFile.close();
}