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
// #include "locAware.h"
// #include "geoUtils.h"
// #include "msgEnum.h"

using std::cout;
using std::endl;
using std::vector;
using std::string;
using std::ifstream;
using std::ofstream;
using std::fstream;

enum msgType
{
    speedData = 1,
};

class BsmGenerator
{
private:
    fstream inputFile;
    
public:
    BsmGenerator(string logfile);
    ~BsmGenerator();

    int getMessageType(string jsonString);
    void readPreloadedCoordinates();
    void getNearestGpsCoordinates();
    string BsmEncoder(string jsonString);
};