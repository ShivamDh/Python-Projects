import requests
from key_wunderland import key_wunderland
from googlemaps.client import Client
from key_google import key_google
from googlemaps.directions import directions
from googlemaps.geocoding import geocode
from math import ceil

startLocation = input("Enter the starting location: ")
endLocation = input("Enter the ending location: ")

mapService = Client(key=key_google)
geocode_start = geocode(mapService, startLocation)
geocode_end = geocode(mapService, endLocation)

requestURL = 'http://api.wunderground.com/api/{0}/geolookup/q/{1},{2}.json'.format(
    key_wunderland, geocode_start[0]['geometry']['location']['lat'], geocode_start[0]['geometry']['location']['lng'])

data = requests.get(requestURL).json()

direction_data = directions(mapService, startLocation, endLocation)
journey_segments = ceil(direction_data[0]['legs'][0]['distance']['value']/50000)
print("\n\nSegment Number: %s" %(journey_segments))

location = {}

print("Current temperature is %s" %(data))

try:
    location = data['location']
except:
    if hasattr(data['response'], 'error'):
        print("No cities matched the city and country entered, check for spelling and capitalization")
    else:
        print("Multiple results exist for the city and country combination entered, have a look:\n")
        for result in data['response']['results']:
            print("Country: {0}\n   City: {1}".format(result['country_name'], result['city']))
        
# location = data['location']['city']
# temp = data['curent_observation']['temp_c']
# print("Current temperature is %s" %(data['current_observation']['temp_c']))
print (requestURL)