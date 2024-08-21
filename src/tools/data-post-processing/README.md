# Software Component Description: Data-Post-Processing
The Data-Post-Processing software component is responsible for post process the data collected during VOICES Pilot 2 Event 2. The post processed data can be feed to Autonomie for eco-metric analysis.

## Work-flow
The Data-Post-Processing composed of one class- (1)DataManager. Data-Post-Processing is an API of DataManager class. The program reads the file name required to post process and the directory to save the post processed file from the configuration file. A function (processRawData()) using an instance of DataManager class is called to post process the data.

### DataManager Class
DataManager has the functionality to create subset csv file based on the start time and end time of the expriment. Processed csv files contain simplified timstamp in ascending order, vehicle type, vehicle speed in meter per second, and road grade data in degree.

## Console output and logging
The Data-Post-Processing can display important messages and log processed data set.

## Requirements
- None

## Configuration
User required to create and specify a JSON formatted configuration file.

## Known issues/limitations
- None