import pandas as pd
import matplotlib.pyplot as plt

class PlotManager:
    def __init__(self, config) -> None:
        self.config = config
        self.groupRunLogFileList = []
        self.soloRunLogFileList = []
        self.groupRunSaveFileNameList = []
        self.soloRunSaveFileNameList = []
    
    def plotSpeedProfile(self):
        
        [self.groupRunLogFileList.append(fileDirectory) for fileDirectory in self.config["VehicleLogFileDirectory"]['Group-Run']]
        [self.soloRunLogFileList.append(fileDirectory) for fileDirectory in self.config["VehicleLogFileDirectory"]['Solo-Run']]
        [self.groupRunSaveFileNameList.append(fileName) for fileName in self.config["SaveFileName"]['Group-Run']]
        [self.soloRunSaveFileNameList.append(fileName) for fileName in self.config["SaveFileName"]['Solo-Run']]
        timeData, vehicleSpeed = ([] for i in range(2))        
        
        def plotDiagram(vehicleLogFileList, saveFileNameList):
            for index, logFileName in enumerate(vehicleLogFileList):
                
                saveFileName = saveFileNameList[index]
                logFileName = '../processed-data' + '/' + logFileName 
                dataFrame = pd.read_csv(logFileName)
                
                for index, row in dataFrame.iterrows():
                    timeData.append(row['Time(s)'])
                    vehicleSpeed.append(row['VehicleSpeed(m/s)'])
                    
                fig, ax1 = plt.subplots()

                ax1.set_xlabel('Time (s)', fontsize=24, fontweight='bold')
                ax1.set_ylabel('Speed (m/s)', fontsize=24, fontweight='bold')
                
                ax1.plot(timeData, vehicleSpeed, label = 'Vehicle Speed', c = "blue")
                # ax1.scatter(timeData, vehicleSpeed, c="blue",  linewidths=4,
                #         marker=".",  edgecolor="none",  s=50, label='Vehicle Speed', zorder=2)
                            
                ax1.legend(loc='upper right', prop={"size": 16})
                ax1.set_title("Speed vs Time Plot", fontsize=20, fontweight='bold')
                fig.tight_layout()  # otherwise the right y-label is slightly clipped
                plt.grid(color='black', linestyle='-', linewidth=0.5)
                # plt.show()
                
                plt.savefig(saveFileName +'-plot.jpg', bbox_inches='tight', dpi=72)
                plt.close(fig)
                
                [li.clear() for li in [timeData, vehicleSpeed]]
                
        if self.groupRunLogFileList:
            plotDiagram(self.groupRunLogFileList, self.groupRunSaveFileNameList)
            
        if self.soloRunLogFileList:
            plotDiagram(self.soloRunLogFileList, self.soloRunSaveFileNameList)


        
        
    