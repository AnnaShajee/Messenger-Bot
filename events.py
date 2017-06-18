#either import or use directly

import requests
import pprint

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
"""
for geo location through quick reply map
pas = {"lat": LATITUDE, "lon": LONGITUDE}
"""
#location and query from user 
place = LOCATION
query = QUERY

parameters = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "m": "foursquare", "v":20161016, "near": place, "limit":3, "query": query}
response = requests.get("https://api.foursquare.com/v2/venues/explore", params = parameters)
        
# Print the status code of the response.
print(response.status_code)
data = response.json()
print(type(data))
context = {'forecast': data['current']['condition']['text'],
'temperature': data['current']['temp_c'],
'wind': data['current']['wind_kph']}
pprint.pprint(context)
