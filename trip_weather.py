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

'''Decodes Google Maps polyline that's encoded using a specific algorithm
available at: http://code.google.com/apis/maps/documentation/polylinealgorithm.html '''

numeric_coords = [[]]
for char in direction_data[0]['overview_polyline']['points']:
    
    # convert to ASCII
    ascii_value = ord(char) - 63
    
    '''a check how many chars per 'piece' of coordinate string
    completing the opposite operation as OR with 32 seen in algorithm'''
    split_check = not (ascii_value & 32)
    
    # and with 31 to reduce ascii value to 5 bits long (truncate if longer)
    ascii_value &= 31
    numeric_coords[-1].append(ascii_value)
    
    if split_check: # apply split check here
        numeric_coords.append([])
    
# cut off any remaining empty array indices
del numeric_coords[-1]

all_numbered_coords = [] # a 1-D list full of all the coordinates 

for individual_coord in numeric_coords:
    coord = 0
    
    for i, chunk in enumerate(individual_coord):                    
        coord |= chunk << (i * 5) 
    
    # if there is a 1 on the right, then coord was negative, invert it
    if coord & 1:
        coord = ~coord
        
    # bit shift 1 right (opposite of 1 left from algorithm), and divide by 1E5 (opposite of x1E5) 
    coord >>= 1
    coord /= 100000.0
                
    all_numbered_coords.append(coord)

# convert 1 dimensional list to a 2 dimensional list with offsets for actual coordinate pairs
the_coords = []
coord_x = 0
coord_y = 0
for i in range(0, len(all_numbered_coords) - 1, 2):
    if all_numbered_coords[i] == 0 and all_numbered_coords[i + 1] == 0:
        continue
    
    coord_x += all_numbered_coords[i]
    coord_y += all_numbered_coords[i + 1]
    the_coords.append((round(coord_x, 6), round(coord_y, 6)))   
    
weather_segments = []
for segment in range(journey_segments + 1):
    coordinate_number = segment//journey_segments * (len(the_coords) - 1)
    weather_segments.append(the_coords[coordinate_number])
    
isForecast = input('\nAre you looking for current conditions (y/n): ')

futureForecast = 0
if isForecast == 'n' or isForecast == 'N':
    print('For how many days in the future are you looking to forecast: ')
    futureForecast = input('1, 2, or 3 days: ')
    
    print('\nWhat kinds of specific details are you looking to get: ')
    print('\t(1) High/Low Temperature \n\t(2) Precipitation \n\t(3) Humidity \n\t(4) Wind')
    choicesSelected = input ('Enter all numbers that apply: ')
    
    print('Lastly, what unit system would you like your results in: \n\t(1) Metric \n\t(2) Imperial')
    units = input('Select one by entering the appropriate number: ')
    while '1' in units and '2' in units:
        units = input('Select only one type, either Metric or Imperial: ')
        
    locationNumber = 1
    
    for xcoord, ycoord in weather_segments:
        requestURL = 'http://api.wunderground.com/api/{0}/conditions/forecast/q/{1},{2}.json'.format(
            key_wunderland, xcoord, ycoord)
    
        data = requests.get(requestURL).json()
        futureForecastDay = data['forecast']['simpleforecast']['forecastday'][int(futureForecast)]
        print('\nLocation Number: {0}'.format(locationNumber))
        print('Conditions: {0}'.format(futureForecastDay['conditions']))
    
        if '1' in choicesSelected:
            if '1' in units:
                print('\tTemperature High: {0}\n\tTemperature Low: {1}'.format(
                    futureForecastDay['high']['celsius'], futureForecastDay['low']['celsius']))
            else:
                print('\tTemperature High: {0}\n\tTemperature Low: {1}'.format(
                    futureForecastDay['high']['fahrenheit'], futureForecastDay['low']['fahrenheit']))
                
        if '2' in choicesSelected:
            print('\tPercent(Chances) of Precipitation: {0}'.format(futureForecastDay['pop']))
            if '1' in units:
                print('\tPrecipitation All Day: {0}\n\tPrecipitation during the Day: {1}'.format(
                    futureForecastDay['qpf_allday']['mm'], futureForecastDay['qpf_day']['mm']))
            else:
                print('\tPrecipitation All Day: {0}\n\tPrecipitation during the Day: {1}'.format(
                    futureForecastDay['qpf_allday']['in'], futureForecastDay['qpf_day']['in']))
                
        if '3' in choicesSelected:
            print('\tAverage Humidity: {0}%'.format(futureForecastDay['avehumidity']))
            
        if '4' in choicesSelected:
            print('\tAverage Wind: \n\t\tDirection/Degrees: {0}/{1}'.format(
                futureForecastDay['avewind']['dir'], futureForecastDay['avewind']['degrees']))
            if '1' in units:
                print('\t\tSpeed: {0}'.format(futureForecastDay['avewind']['kph']))
            else:
                print('\t\tSpeed: {0}'.format(futureForecastDay['avewind']['mph']))
            print('\tMax Wind: \n\t\tDirection/Degrees: {0}/{1}'.format(
                futureForecastDay['maxwind']['dir'], futureForecastDay['maxwind']['degrees']))
            if '1' in units:
                print('\t\tSpeed: {0}'.format(futureForecastDay['maxwind']['kph']))
            else:
                print('\t\tSpeed: {0}'.format(futureForecastDay['maxwind']['mph']))
        
        locationNumber += 1
else:
    print('What current details would you like about your trip:')
    for xcoord, ycoord in weather_segments:
        requestURL = 'http://api.wunderground.com/api/{0}/conditions/forecast/q/{1},{2}.json'.format(
            key_wunderland, xcoord, ycoord)
    
        data = requests.get(requestURL).json()
    
    