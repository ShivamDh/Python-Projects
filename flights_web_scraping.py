from requests import get

flight_type = input('What type of flight is this:\n\t(1) One Way\n\t(2) Return Trip\n ')

start = input('Enter the 3 digit airport code of the starting location: ')

end = input('Enter the 3 digit airport code of the ending location: ')

date_1 = input('Enter the start date of the journey - DD/MM/YYYY: ')

date_2 = ''

if flight_type == 2:
	date_2 = input('Enter the end date of the journey - DD/MM/YYYY: ')
	
csv_headers = 'Starts (' + start.upper() + '),'
csv_headers += 'Ends (' + end.upper() + '),Time' 

if flight_type == 2:
	csv_headers = 'Starts (' + end.upper() + '),'
	csv_headers += 'Ends (' + start.upper() + '),Time'

csv_headers += ',Price\n'

#f = open("flights.csv", "w")

expedia_url = 'https://www.expedia.ca/Flights-Search?trip=oneway&leg1=from%3AJFK%2Cto%3ALAX%2Cdeparture%3A19%2F06%2F2018TANYT&passengers=adults%3A1%2Cchildren%3A0%2Cseniors%3A0%2Cinfantinlap%3AY&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'

if flight_type == 1:
	expedia_url += '?trip=oneway'
else:
	expedia_url += '?trip=roundtrip'
	
expedia_url += '&leg1=from%3A' + start + '%2Cto%3A' + end + '%2C'

expedia_url += 'departure%3A' + date_1[0:2] + '%2F' + date_1[3:5] + '%2F' + date_1[6:10] + 'TANYT'

expedia_url += '&passengers=adults%3A1&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'

expedia_response = get(expedia_url)