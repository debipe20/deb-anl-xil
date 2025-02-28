import json
from pprint import pprint
from urllib.request import urlopen

# GeoReferencedPredictions

lat = 41.84581787248484
lng = -88.3399575438551
heading = 90

#Kearney Rd  Reference Point 
# lat =  41.7103948768268
# lng = -87.9920446449095
# heading = 358

urlGRP =    str('https://anlab.traffictechservices.com:5833/APhA/Services/GeoReferencedPredictions?username=ArgonneNL&password=jjM5sACr') \
          + str('&latitude=') + str(lat) \
          + str('&longitude=') + str(lng) \
          + str('&heading=') + str(heading) + str('&returnJSON=true')
          
u = urlopen(urlGRP)
respGRP = json.loads(u.read().decode('utf-8'))
pprint(respGRP)

# TragetedPredictions

# targetRegion = 'Kane%20County'
# targetScnr = 25
# targetApproach = 2

# url =   str('https://anlab.traffictechservices.com:5833/APhA/Services/TargetedPredictions?username=ArgonneNL&password=jjM5sACr') \
#       + str('&targetRegion=') + str(targetRegion) \
#       + str('&targetScnr=') + str(targetApproach) \
#       + str('&targetApproach=') + str(targetApproach) + str('&returnJSON=true') 

# u = urlopen(url)
# respTP = json.loads(u.read().decode('utf-8'))
# pprint(respTP)

# 'https://anlab.traffictechservices.com:5833/APhA/Services/GeoReferencedPredictions?username=ArgonneNL&password=jjM5sACr'
# 'https://anlab.traffictechservices.com:5833/APhA/Services/TargetedPredictions?username=ArgonneNL&password=jjM5sACr'