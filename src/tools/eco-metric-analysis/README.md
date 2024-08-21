# Software Component Description: Data-Analyzer
The Data-Analyzer software component is responsible for analyzing the data collected during VOICES Pilot 2 Event 2 using Argonne's DAQ system. 

## Work-flow
The Data-Analyzer composed of one class- (1)DataAnalyzer. Data-Analyzer program reads the file name required to analyze and call required functions using an instance of DataAnalyzer class to analyze the data.

### DataAnalyzer Class
DataAnalyzer has the functionality to analyze the data for different parameters such as speed profile, transmission oil temperature, state of charge, etc. and generate diagrams.

## Console output and logging
The Data-Analyzer can display important messages and store the diagrams.

## Requirements
- None

## Configuration
User required to specify the directory of the file contain data in the configuration file.

## Known issues/limitations
- None