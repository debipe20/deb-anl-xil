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
#include <cmath>
// using namespace GeoUtils;
// using namespace MsgEnum;

BsmGenerator::BsmGenerator(string logfile)
{
    inputFile.open(logfile, ios::in);    
    readPreloadedCoordinates();
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
    string subString{};
    int lineNo{};

    while (getline(inputFile, line))
    {
        lineNo++;
        stringstream strToSplit(line.c_str());

        if (lineNo > 1)
        {
            for (int index = 0; getline(strToSplit, subString, ','); index++)
            {
                if (index == 5)
                    latitudeList.push_back(subString);
                
                elif (index == 6)
                    longitudeList.push_back(subString);

                elif (index == 7)
                    elevationList.push_back(subString);

                elif (index == 9)
                    headingList.push_back(subString);
            }
        }
    }
}

void BsmGenerator::getNearestGpsCoordinates(double currentSpeed)
{
    double currentTime =  getPosixTimestamp();
    double travelDistance{};
    double elapsedTimeStep{};
    double estimatedDistance{};
    double estimatedDistanceNext{};

    if (!previousTimeStampSetStatus)
    {    
        previousTimeStamp = currentTime - 0.1;
        previousTimeStampSetStatus = true;
    }

    elapsedTimeStep = currentTime - previousTimeStamp;
    travelDistance = currentSpeed * elapsedTimeStep;

    for (size_t i = previousIndex + 1; i < latitudeList.size() - 1; i++)
    {
        estimatedDistance = haversineDistance(latitudeList[previousIndex], longitudeList[previousIndex], latitudeList[i], longitudeList[i]);
        estimatedDistanceNext = haversineDistance(latitudeList[previousIndex], longitudeList[previousIndex], latitudeList[i+1], longitudeList[i+1]);
    
        if((estimatedDistance < travelDistance) && (estimatedDistanceNext < travelDistance))
            continue;

        else if ((estimatedDistance <= travelDistance) && (estimatedDistanceNext > travelDistance))
        {
            previousIndex = 
        }
    
    }
}

double BsmGenerator::haversineDistance(double lat1, double lon1,double lat2, double lon2)
{
    double lattitudeDifference{};
    double longitudeDifference{};
    double rad{6371};
    double distance{};
    double intermediateCalculation{};

    // distance between latitudes and longitudes
    lattitudeDifference = (lat2 - lat1) * M_PI / 180.0;
    longitudeDifference = (lon2 - lon1) * M_PI / 180.0;

    // convert to radians
    lat1 = (lat1)*M_PI / 180.0;
    lat2 = (lat2)*M_PI / 180.0;

    // apply formula
    intermediateCalculation = pow(sin(lattitudeDifference / 2), 2) + pow(sin(longitudeDifference / 2), 2) * cos(lat1) * cos(lat2);

    distance = 2 * rad * asin(sqrt(intermediateCalculation)) * 1000.0;

    return distance;
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