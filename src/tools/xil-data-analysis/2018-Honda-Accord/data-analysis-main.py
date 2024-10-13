import json
from PlotManager import PlotManager

def main():
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    plot_manager = PlotManager(config)
    plot_manager.generate_plots()

if __name__ == "__main__":
    main() 