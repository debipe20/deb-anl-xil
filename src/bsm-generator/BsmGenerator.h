/*
**********************************************************************************

**********************************************************************************
  BsmGenerator.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is header file for BsmGenerator.cpp
*/

#pragma once
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <fstream>
#include "json/json.h"
#include "AsnJ2735Lib.h"
#include "dsrcConsts.h"
// #include "locAware.h"
// #include "geoUtils.h"
// #include "msgEnum.h"

using std::cout;
using std::endl;
using std::fstream;
using std::ifstream;
using std::ios;
using std::ofstream;
using std::string;
using std::stringstream;
using std::vector;

enum msgType
{
    speedData = 1,
};

class BsmGenerator
{
private:
    string vehicleId{};
    int previousIndex{0};
    double previousTimeStamp{};
    double currentLatitude{};
    double currentLongitude{};
    double currentElevation{};
    double currentSpeed{};
    double currentHeading{};
    bool previousTimeStampSetStatus{false};
    vector <double> latitudeList{};
    vector <double> longitudeList{};
    vector <double> elevationList{};
    vector <double> headingList{};
    fstream inputFile;

public:
    BsmGenerator(string logfile, string vehId);
    ~BsmGenerator();

    int getMessageType(string jsonString);
    void readPreloadedCoordinates();
    void getNearestGpsCoordinates();
    double haversineDistance(double lat1, double lon1,double lat2, double lon2);
    string BsmEncoder(string jsonString);
};