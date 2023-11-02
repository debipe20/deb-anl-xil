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
#include "Timestamp.h"
#include <cmath>
// using namespace GeoUtils;
// using namespace MsgEnum;

#define OneByTenMicroDegree_To_Degree 10000000
#define Deca_Conversion 10
#define MPS_TO_KPH_CONVERSION 3.6
#define SECOND_MILISECOND_CONVERSION 1000

BsmGenerator::BsmGenerator(string logfile)
{
    inputFile.open(logfile, ios::in);
    outputFile.open("estimated-data.csv");
    outputFile << "lattitude"
               << ","
               << "longitude"
               << ","
               << "elevation"
               << ","
               << "speed"
               << ","
               << "heading"
               << "\n";
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
                    latitudeList.push_back(stod(subString));

                else if (index == 6)
                    longitudeList.push_back(stod(subString));

                else if (index == 7)
                    elevationList.push_back(stod(subString));

                else if (index == 9)
                {
                    headingList.push_back(stod(subString));
                    break;
                }
            }
        }
    }
}

void BsmGenerator::getNearestGpsCoordinates()
{
    double currentTime = getPosixTimestamp();
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

    for (size_t currentIndex = previousIndex + 1; currentIndex < latitudeList.size() - 1; currentIndex++)
    {
        estimatedDistance = haversineDistance(latitudeList[previousIndex], longitudeList[previousIndex], latitudeList[currentIndex], longitudeList[currentIndex]);
        estimatedDistanceNext = haversineDistance(latitudeList[previousIndex], longitudeList[previousIndex], latitudeList[currentIndex + 1], longitudeList[currentIndex + 1]);

        if ((estimatedDistance < travelDistance) && (estimatedDistanceNext < travelDistance))
            continue;

        else if ((estimatedDistance >= travelDistance) && (estimatedDistanceNext >= travelDistance))
        {
            previousIndex = static_cast<int>(currentIndex);
            currentLatitude = latitudeList[currentIndex];
            currentLongitude = longitudeList[currentIndex];
            currentElevation = elevationList[currentIndex];
            currentHeading = headingList[currentIndex];
            break;
        }

        else if ((estimatedDistance <= travelDistance) && (estimatedDistanceNext > travelDistance))
        {
            previousIndex = static_cast<int>(currentIndex);
            currentLatitude = latitudeList[currentIndex];
            currentLongitude = longitudeList[currentIndex];
            currentElevation = elevationList[currentIndex];
            currentHeading = headingList[currentIndex];
            break;
        }

        else if ((estimatedDistance < travelDistance) && (estimatedDistanceNext >= travelDistance))
        {
            previousIndex = static_cast<int>(currentIndex + 1);
            currentLatitude = latitudeList[currentIndex + 1];
            currentLongitude = longitudeList[currentIndex + 1];
            currentElevation = elevationList[currentIndex + 1];
            currentHeading = headingList[currentIndex + 1];
            break;
        }
    }
}

double BsmGenerator::haversineDistance(double lat1, double lon1, double lat2, double lon2)
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

string BsmGenerator::BsmEncoder(string jsonString)
{
    stringstream payloadstream{};
    string bsmMessagePayload{};
    /// buffer to hold message payload
    size_t bufSize = DsrcConstants::maxMsgSize;
    vector<uint8_t> buf(bufSize, 0);
    // basicVehicle.json2BasicVehicle(jsonString);
    /// dsrcFrameIn to store input to UPER encoding function
    Frame_element_t dsrcFrameIn;
    dsrcFrameIn.reset();

    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};

    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
    delete reader;

    if(parsingSuccessful)
        currentSpeed = jsonObject["Speed"].asDouble();
    
    getNearestGpsCoordinates();
    setMsgCount();

    /// manual input bsmIn
    dsrcFrameIn.dsrcMsgId = MsgEnum::DSRCmsgID_bsm;
    BSM_element_t &bsmIn = dsrcFrameIn.bsm;
    bsmIn.msgCnt = static_cast<uint8_t>(msgCount);
    bsmIn.id = 0xf03ad610;
    bsmIn.timeStampSec = static_cast<int16_t>(getMsOfMinute() / SECOND_MILISECOND_CONVERSION);
    bsmIn.latitude = DsrcConstants::unit2damega<int32_t>(currentLatitude);
    bsmIn.longitude = DsrcConstants::unit2damega<int32_t>(currentLongitude);
    bsmIn.elevation = DsrcConstants::unit2deca<int32_t>(currentElevation);
    bsmIn.yawRate = 0;
    bsmIn.vehLen = 1200;
    bsmIn.vehWidth = 300;
    bsmIn.speed = DsrcConstants::kph2unit<uint16_t>(currentSpeed * MPS_TO_KPH_CONVERSION);
    bsmIn.heading = DsrcConstants::heading2unit<uint16_t>(currentHeading);

    /// encode BSM payload
    size_t payload_size = AsnJ2735Lib::encode_msgFrame(dsrcFrameIn, &buf[0], bufSize);
    if (payload_size > 0)
    {
        for (size_t i = 0; i < payload_size; i++)
            payloadstream << std::uppercase << std::setw(2) << std::setfill('0') << std::hex << static_cast<unsigned int>(buf[i]);
    }

    bsmMessagePayload = payloadstream.str();
    loggingData();

    return bsmMessagePayload;
}

/*
	- Method for obtaining millisecond of a minute based on GMT(UTC) time
*/
int BsmGenerator::getMsOfMinute()
{
	int msOfMinute{};

	time_t curr_time;
	curr_time = time(NULL);
	tm *tm_gmt = gmtime(&curr_time);

	int currentSecond = tm_gmt->tm_sec;

	msOfMinute = currentSecond * static_cast<int>(SECOND_MILISECOND_CONVERSION);

	return msOfMinute;
}

void BsmGenerator::setMsgCount()
{
    if (msgCount < 127)
        msgCount ++;
    
    else msgCount = 1;
}

void BsmGenerator::loggingData()
{
    outputFile << fixed << showpoint << setprecision(8) << currentLatitude << "," << currentLongitude << ","
               << fixed << showpoint << setprecision(2) << currentElevation << "," << currentSpeed << "," << currentHeading << "\n";
}

BsmGenerator::~BsmGenerator()
{
    inputFile.close();
    outputFile.close();
}