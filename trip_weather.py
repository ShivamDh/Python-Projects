import requests
from key_wunderland import key_wunderland
from googlemaps.client import Client
from key_google import key_google
from googlemaps.directions import directions
from googlemaps.geocoding import geocode
from math import ceil

print("Hint: Enter as descriptive as an address possible (preferably add cities to address)")
startLocation = input("Enter the starting location: ")
endLocation = input("Enter the ending location: ")

mapService = Client(key=key_google)
geocode_start = geocode(mapService, startLocation)
geocode_end = geocode(mapService, endLocation)

direction_data = directions(mapService, startLocation, endLocation)
journey_segments = ceil(direction_data[0]['legs'][0]['distance']['value']/50000)
print("\n\nSegment Number: %s" %(journey_segments))

latitude_difference = (geocode_end[0]['geometry']['location']['lat'] - geocode_start[0]['geometry']['location']['lat'])/journey_segments
longitude_difference = (geocode_end[0]['geometry']['location']['lng'] - geocode_start[0]['geometry']['location']['lng'])/journey_segments 

requestURL = 'http://api.wunderground.com/api/{0}/geolookup/q/{1},{2}.json'.format(
    key_wunderland, geocode_start[0]['geometry']['location']['lat'], geocode_start[0]['geometry']['location']['lng'])

data = requests.get(requestURL).json()

location = {}

print("Current temperature is {0}".format(direction_data))
print (requestURL)

def decode(point_str):
    '''Function that will decodes Google Maps polyline that's encoded using a specific algorithm
    available at: http://code.google.com/apis/maps/documentation/polylinealgorithm.html
    Method gets a string parameter that is the polyline and returns a pair of (latitude, longitude)
    '''
    
    all_all_numbered_coords = [[]]
    for char in point_str:
        
#         convert to ASCII
        ascii_value = ord(char) - 63
        
#         a check how many chars per 'piece' of coordinate string
#         completing the opposite operation as OR with 32 seen in algorithm
        split_check = not (ascii_value & 32)
#         and with 31 to reduce ascii value to 5 bits long (truncate if longer)
        ascii_value &= 31
        all_all_numbered_coords[-1].append(ascii_value)
        
        if split_check: #apply split check here
            all_all_numbered_coords.append([])
        
#     cut off any remaining empty array indices
   return

# the_coords = decode(direction_data[0]['overview_polyline']['points'])
# for xcoord, ycoord in the_coords:
    # print("%s %s" %(xcoord, ycoord))
    
# print("%s" %(len(the_coords)))