import json
import time
from urllib.request import urlopen

# Function to fetch and print intersection data
def fetch_intersection_data():
    # GeoReferencedPredictions
    lat = 41.84581787248484
    lng = -88.3399575438551
    heading = 90

    urlGRP = (
        str('https://anlab.traffictechservices.com:5833/APhA/Services/GeoReferencedPredictions?username=ArgonneNL&password=jjM5sACr')
        + str('&latitude=') + str(lat)
        + str('&longitude=') + str(lng)
        + str('&heading=') + str(heading)
        + str('&returnJSON=true')
    )
    
    try:
        u = urlopen(urlGRP)
        respGRP = json.loads(u.read().decode('utf-8'))

        # Check and process response
        if 'Data' in respGRP and 'Items' in respGRP['Data']['Data']:
            for item in respGRP['Data']['Data']['Items']:
                intersection_name = item['Intersections']['Items'][0]['Name']
                print(f"Intersection Name: {intersection_name}")
                
                phases = item['Intersections']['Items'][0]['Phases']['Items']
                for phase in phases:
                    bulb_color = phase['BulbColor']
                    duration_in_state = phase['DurationInState']
                    print(f"  - Phase: {phase['PhaseNr']}, Bulb Color: {bulb_color}, Duration in State: {duration_in_state}s")
                    
                    predictive_changes = phase.get('PredictiveChanges', {}).get('Items', [])
                    for change in predictive_changes:
                        change_color = change['BulbColor']
                        time_to_change = change['TimeToChange']
                        print(f"    -> Will change to {change_color} in {time_to_change}s")
        else:
            print("No intersection data available.")
    except Exception as e:
        print(f"Error fetching data: {e}")

# Loop to continuously fetch data
while True:
    fetch_intersection_data()
    print("\n--- Fetching again in 5 seconds ---\n")
    time.sleep(5)  # Wait 5 seconds before the next request
