import json
from DiagnosticSignalManager import Diagnostic
from Decoder import Decoder

def main():
    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()
    
    # signals = [['0x245', '', (3, 3), (0, -1), 0.5, 0],
    #        ['7DA', '04618a', (4, 5), (0, -1), 0.01, -327.68],
    #        ['7DA', '0x06 61 81', (6, 7), (0, -1), 0.1, 0]]
    
    signalsList = []
    
    for signalInfo in config["SignalInformation"]:
        signalsList.append([signalInfo['arbid'], signalInfo['message_start'], (signalInfo['start_byte'], signalInfo['end_byte']), (signalInfo['start_bit'], signalInfo['end_bit']), signalInfo['scale'], signalInfo['offset']])
    print(signalsList)
    
    all_data_path = config["FileName"]
    print(all_data_path)
    
    # The *signal syntax unpacks the elements of each signal in the signals list and passes them as separate arguments to the Diagnostic constructor and create instance/object of Diagnostic for each signal
    knownSignalsList = [Diagnostic(*signal) for signal in signalsList]
    first_bits_and_lengths = [signal.get_bits() for signal in knownSignalsList]
    
    for signal in knownSignalsList:
        signal.set_data_path(all_data_path)
        
    can_decoder = Decoder(all_data_path, full_csv=True) # Keep full_csv=True here
    signal_decoders = [Decoder(signal.data_path, full_csv=False) for signal in knownSignalsList] # Set full_csv False
    
    
    
    
    
    
if __name__ == "__main__":
    main()