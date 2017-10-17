from requests import get
from bs4 import BeautifulSoup as soup
import json

flight_type = input('What type of flight is this:\n\t(1) One Way\n\t(2) Return Trip\n ')

start = input('Enter the 3 digit airport code of the starting location: ')

end = input('Enter the 3 digit airport code of the ending location: ')

date_1 = input('Enter the start date of the journey - DD/MM/YYYY: ')

date_2 = ''

if flight_type == 2:
	date_2 = input('Enter the end date of the journey - DD/MM/YYYY: ')
	
csv_headers = 'Website, Start (' + start.upper() + '),'
csv_headers += 'End (' + end.upper() + '),Duration' 

if flight_type == 2:
	csv_headers = 'Start (' + end.upper() + '),'
	csv_headers += 'End (' + start.upper() + '),Duration'

csv_headers += ',Price\n'

f = open("flights.csv", "w")
f.write(csv_headers)

expedia_url = 'https://www.expedia.ca/Flights-Search?trip=oneway&leg1=from%3AJFK%2Cto%3ALAX%2Cdeparture%3A19%2F06%2F2018TANYT&passengers=adults%3A1%2Cchildren%3A0%2Cseniors%3A0%2Cinfantinlap%3AY&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'

if flight_type == 1:
	expedia_url += '?trip=oneway'
else:
	expedia_url += '?trip=roundtrip'
	
expedia_url += '&leg1=from%3A' + start + '%2Cto%3A' + end + '%2C'

expedia_url += 'departure%3A' + date_1[0:2] + '%2F' + date_1[3:5] + '%2F' + date_1[6:10] + 'TANYT'

expedia_url += '&passengers=adults%3A1&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'

expedia_response = get(expedia_url)

expedia_soup = soup(expedia_response.text, 'html.parser')

continued_results_divs = expedia_soup.find_all('div', {'id': 'originalContinuationId'})

if len(continued_results_divs) > 0:
	expedia_results_id = continued_results_divs[0].text.strip()
	expedia_results_url = 'https://www.expedia.ca/Flight-Search-Paging'
	expedia_results_url += '?c=' + continued_results_id
	expedia_results_url += '&is=1&sp=asc&cz=200&cn=0'
	
	expedia_results_response = get(expedia_more_results_url)
	expedia_json = json.loads(expedia_results_response.text)
	
	flights = expedia_json['content']['legs']
	flight_keys = list(flights)
	
	# send another Expedia request to gather second leg journeys
	if flight_type == 2:
		expedia_results_2_url = expedia_results_url.replace(
			'is=1',
			'is=0&fl0=' + flight_keys[0]
		)
		
		expedia_results_2_url = expedia_results_2_url.replace('ul=0', 'ul=1')
		
		expedia_results_2_response = get(expedia_results_2_url)
		expedia_2_json = json.loads(expedia_results_2_response.text)
		
		flights_2 = expedia_2_json['content']['legs']
		flight_2_keys = list(flights_2)
	
	for flight in flight_keys:
		start_time = flight['departureTime']['time']
		end_time = flight['arrivalTime']['time']
		
		duration = str(flight['duration']['hours']) + 'h ' + str(flight['duration']['minutes']) + 'm'
		price = flight['price']['formattedPrice']
		
		f.write('Expedia,' + start_time + ',' + end_time + ',' + duration + ',' + price + '\n')
	
else:
	flights = expedia_soup.find_all('li', {'class': 'flight-module'})
	
	for flight in flights:
		start_time_span = flight.find_next('span', {'data-test-id': 'departure-time'})
		if start_time_span is None:
			start_time = ''
		else:
			start_time = start_time_span.text.strip()
		
		end_time_span = flight.find_next('span', {'data-test-id': 'arrival-time'})
		if end_time_span is None:
			end_time = ''
		else:
			end_time = end_time_span.text.strip()
		
		duration_span = flight.find_next('span', {'data-test-id': 'duration'})
		if duration_span is None:
			duration = ''
		else:
			duration = duration_span.text.strip()
		
		price_column_div = flight.find_next('div', {'data-test-id': 'price-column'})   
		if price_column_div is None:
			price = ''
		else:
			price = price_column_div.div.findAll('span')[-1].text.strip() 
			
		f.write('Expedia,' + start_time + ',' + end_time + ',' + duration + ',' + price + '\n')	
	

f.close()
	