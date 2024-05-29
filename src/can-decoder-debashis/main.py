import json

def main():
    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()
    
    signals = [['0x245', '', (3, 3), (0, -1), 0.5, 0],
           ['7DA', '04618a', (4, 5), (0, -1), 0.01, -327.68],
           ['7DA', '0x06 61 81', (6, 7), (0, -1), 0.1, 0]]
    
    all_data_path = config["FileName"]
    print(all_data_path)
    

if __name__ == "__main__":
    main()