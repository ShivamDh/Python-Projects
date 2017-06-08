import requests
from key_wunderland import key_wunderland

city = input("Test a city of whose weather you want: ")
country = input("To double check, enter the country: ")

requestURL = 'http://api.wunderground.com/api/{0}/geolookup/conditions/q/{1}/{2}.json'.format(key_wunderland, country, city)

data = requests.get(requestURL).json()
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