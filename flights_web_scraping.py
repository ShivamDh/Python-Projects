from requests import get, post
from bs4 import BeautifulSoup as soup
import json

flight_type = input('What type of flight is this:\n\t(1) One Way\n\t(2) Return Trip\n ')

start = input('Enter the 3 digit airport code of the starting location: ')

end = input('Enter the 3 digit airport code of the ending location: ')

date_1 = input('Enter the start date of the journey - DD/MM/YYYY: ')

date_2 = ''

if flight_type == '2':
	date_2 = input('Enter the end date of the journey - DD/MM/YYYY: ')
	
csv_headers = 'Website,Airline,Start({0}),End({1}),Duration,Stops'.format(start.upper(), end.upper())

if flight_type == '2':
	csv_headers += ',Airline,Start ({0}),End({1}),Duration,Stops'.format(end.upper(), start.upper())

csv_headers += ',Price\n\n'

f = open("flights.csv", "w")
f.write(csv_headers)

'''
	Web scraping from Expedia
'''

expedia_url = 'https://www.expedia.ca/Flights-Search'

if flight_type == '1':
	expedia_url += '?trip=oneway'
else:
	expedia_url += '?trip=roundtrip'
	
expedia_url += '&leg1=from%3A{0}%2Cto%3A{1}%2C'.format(start, end)

expedia_url += 'departure%3A{0}%2F{1}%2F{2}TANYT'.format(date_1[0:2], date_1[3:5], date_1[6:10])

if flight_type == '2':
	expedia_url += '&leg2=from%3A{0}%2Cto%3A{1}%2C'.format(end, start)
	expedia_url += 'departure%3A{0}%2F{1}%2F{2}TANYT'.format(date_2[0:2], date_2[3:5], date_2[6:10])

expedia_url += '&passengers=adults%3A1&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'

expedia_response = get(expedia_url)

expedia_soup = soup(expedia_response.text, 'html.parser')

continued_results_divs = expedia_soup.find_all('div', {'id': 'originalContinuationId'})

if len(continued_results_divs) > 0:
	expedia_results_id = continued_results_divs[0].text.strip()
	expedia_results_url = 'https://www.expedia.ca/Flight-Search-Paging?c={0}&is=1&sp=asc&cz=200&cn=0&ul=0'.format(expedia_results_id)
	
	expedia_results_response = get(expedia_results_url)
	expedia_json = json.loads(expedia_results_response.text)
	
	flights = expedia_json['content']['legs']
	flight_keys = list(flights)
	
	# send another Expedia request to gather second leg journeys
	if flight_type == '2':
		expedia_results_2_url = expedia_results_url.replace(
			'is=1',
			'is=0&fl0=' + flight_keys[0]
		)
		
		expedia_results_2_url = expedia_results_2_url.replace('ul=0', 'ul=1')
		
		expedia_results_2_response = get(expedia_results_2_url)
		expedia_2_json = json.loads(expedia_results_2_response.text)
		
		flights_2 = expedia_2_json['content']['legs']
		
		flights_2 = sorted(flights_2.items(), key=lambda x: x[1]['price']['exactPrice'])
		flights_2 = flights_2[:10]
		
		flights = sorted(flights.items(), key=lambda x: x[1]['price']['exactPrice'])
		flights = flights[:10]
		
		cheapest_first_leg_flight = flights[0][1]['price']['exactPrice']
		
		for flight in flights:
			start_time = flight[1]['departureTime']['time']
			end_time = flight[1]['arrivalTime']['time']
			
			duration = str(flight[1]['duration']['hours']) + 'h ' + str(flight[1]['duration']['minutes']) + 'm'
			price = flight[1]['price']['formattedPrice'][0:2] + flight[1]['price']['totalPriceAsDecimalString']
			
			airline = flight[1]['carrierSummary']['airlineName']
			if airline == '':
				airline = 'Multiple Airlines'
			
			stops = flight[1]['formattedStops']
			if stops == '0':
				stops = 'Nonstop'
			elif stops == '1':
				stops += ' Stop'
			else:
				stops += ' Stops'
			
			for flight_2 in flights_2:
				start_time_2 = flight_2[1]['departureTime']['time']
				end_time_2 = flight_2[1]['arrivalTime']['time']
			
				duration_2 = str(flight_2[1]['duration']['hours']) + 'h ' + str(flight_2[1]['duration']['minutes']) + 'm'
				
				airline_2 = flight_2[1]['carrierSummary']['airlineName']
				if airline_2 == '':
					airline_2 = 'Multiple Airlines'
				
				stops_2 = flight_2[1]['formattedStops']
				if stops_2 == '0':
					stops_2 = 'Nonstop'
				elif stops_2 == '1':
					stops_2 += ' Stop'
				else:
					stops_2 += ' Stops'
				
				f.write('Expedia,{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}'.format(
					airline, start_time, end_time, duration, stops,
					airline_2, start_time_2, end_time_2, duration_2, stops_2
				))
				
				price_2 = flight_2[1]['price']['exactPrice'] + flight[1]['price']['exactPrice'] - cheapest_first_leg_flight
				final_price = flight_2[1]['price']['formattedPrice'][0:2] + "{:.2f}".format(float(price_2))
				
				f.write(',{0}\n'.format(final_price))
		
	else:
		for key in flights:
			start_time = flights[key]['departureTime']['time']
			end_time = flights[key]['arrivalTime']['time']
			
			duration = str(flights[key]['duration']['hours']) + 'h ' + str(flights[key]['duration']['minutes']) + 'm'
			price = flights[key]['price']['formattedPrice'][0:2] + flights[key]['price']['totalPriceAsDecimalString']
			
			airline = flights[key]['carrierSummary']['airlineName']
			if airline == '':
				airline = 'Multiple Airlines'
			
			stops = flights[key]['formattedStops']
			if stops == '0':
				stops = 'Nonstop'
			elif stops == '1':
				stops += ' Stop'
			else:
				stops += ' Stops'
			
			f.write('Expedia,{0},{1},{2},{2},{4},{5}\n'.format(airline, start_time, end_time, duration, stops, price))
	
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
		
		airline_span = flight.find_next('div', {'data-test-id': 'airline-name'})
		if airline_span is None:
			airline = ''
		else:
			airline = airline_span.text.strip()
			
		stops_span = duration_span.find_next_sibling('span') 
		if stops_span is None or not stops_span.has_attr('data-test-num-stops'):
			stops = ''
		else:
			stops = stops_span.text.strip().replace('(', '').replace(')','')
		
		price_column_div = flight.find_next('div', {'data-test-id': 'price-column'})   
		if price_column_div is None:
			price = ''
		else:
			price_spans = price_column_div.div.findAll('span')
			if len(price_spans) == 0:
				price = ''
			else:
				price = price_spans[-1].text.strip().replace(',', '')
			
		f.write('Expedia,{0},{1},{2},{3},{4},{5}\n'.format(airline, start_time, end_time, duration, stops, price))


'''
	Web scraping from Kayak
'''
	
kayak_home_url = 'https://www.kayak.com'
kayak_home_response = get(kayak_home_url)
kayak_cookies = kayak_home_response.cookies

kayak_search_url = kayak_home_url + '/s/horizon/flights/results/FlightSearchPoll'

kayak_date_1 = date_1[6:10] + '-' + date_1[3:5] + '-' + date_1[0:2]

kayak_url_to_append = 'flights/{0}-{1}/{2}'.format(start.upper(), end.upper(), kayak_date_1)

if flight_type == '2':
	kayak_date_2 = date_2[6:10] + '-' + date_2[3:5] + '-' + date_2[0:2]
	kayak_url_to_append += '/' + kayak_date_2

referer = kayak_home_url + '/' + kayak_url_to_append

headers = {
    'Host': 'www.kayak.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': referer,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest'
}

params = {
    'searchId':'',
    'poll':'true',
    'pollNumber':'0',
    'applyFilters':'true',
    'filterState':'',
    'useViewStateFilterState':'false',
    'pageNumber':'1',
    'append':'false',
    'pollingId':'593601',  #interesting. explore further
    'requestReason':'POLL',
    'isSecondPhase':'false',
    'textAndPageLocations':'bottom,right',
    'displayAdPageLocations':'none',
    'existingAds':'false',
    'activeLeg':'-1',
    'view':'list',
    'renderPlusMinusThreeFlex':'false',
    'renderAirlineStopsMatrix':'false',
    'renderFlexHeader':'true',
    'tab':'flights',
    'pageOrigin':'F..FD..M0',
    'src':'',
    'searchingAgain':'',
    'c2s':'',
    'po':'',
    'personality':'',
    'provider':'',
    'isMulticity':'false',
    'flex_category':'exact',
    'depart_date':kayak_date_1,
    'return_date':kayak_date_2,
    'oneway':'false',
    'origincode':start.upper(),  #change accordingly
    'origin':start.upper(), #change accordingly
    'origin_location':'', #change accordingly
    'origin_code':'', #change accordingly
    'nearby_origin':'false',
    'destination':end.upper(), #change accordingly
    'destination_location':'', #change accordingly
    'destination_code':end.upper(), #change accordingly
    'nearby_destination':'false',
    'countrySearch':'false',
    'depart_date_canon':kayak_date_1, #change accordingly
    'return_date_canon':kayak_date_2, #change accordingly
    'travelers':'1',
    'adults':'1',
    'seniors':'0',
    'youth':'0',
    'child':'0',
    'seatInfant':'0',
    'lapInfant':'0',
    'cabin':'e',
    'cabinDisplayType':'Economy',
    'vertical':'flights',
    'url':kayak_url_to_append,
    'id':'',
    'navigateToResults':'false',
    'ajaxts':'',
    'scriptsMetadata':'',
    'stylesMetadata':'',
}

kayak_response = post(kayak_search_url, headers = headers, data = params, cookies = kayak_cookies)

kayak_soup = soup(json.loads(kayak_response.text)['content'], 'html.parser')

flights = kayak_soup.find_all('div', {'class': 'Flights-Results-FlightResultItem'}) 

for flight in flights:
	start_time_divs = flight.find_all('div', {'class': 'depart'})
	if len(start_time_divs) < 1:
		start_time = ''
	else:
		start_time = start_time_divs[0].div.text.strip().replace('\n', '')
		
	end_time_divs = flight.find_all('div', {'class': 'return'})
	if len(end_time_divs) < 1:
		end_time = ''
	else:
		end_time = end_time_divs[0].div.text.strip().replace('\n', '')
		
	duration_divs = flight.find_all('div', {'class': 'duration'})
	if len(duration_divs) < 1:
		duration = ''
	else:
		duration = duration_divs[0].div.text.strip().replace('\n', '')

	airline_divs = flight.find_all('div', {'class': 'carrier'})
	if len(airline_divs) < 1:
		airline = ''
	else:
		airline_inner_divs = airline_divs[0].find_all('div')
		if len(airline_inner_divs) > 0:
			airline = airline_inner_divs[-1].text.strip()
		else:
			airline = ''
			
	stops_divs = flight.find_all('div', {'class': 'stops'})
	if len(stops_divs) < 1:
		stops = ''
	else:
		stops_inner_spans = stops_divs[0].find_next('span', {'class': 'axis'})
		if stops_inner_spans is None:
			stops = ''
		else:
			num_stops = len(stops_inner_spans.find_all('span', {'class': 'dot'}))
			if num_stops == 0:
				stops = 'Nonstop'
			elif num_stops == 1:
				stops = '1 stop'
			else:
				stops = '{0} stops'.format(len(num_stops))
	
	price_spans = flight.find_next('span', {'class': 'price'})
	if price_spans is None:
		price = ''
	else:
		price = price_spans.text.strip()

	f.write('Kayak,{0},{1},{2},{3},{4},{5}\n'.format(airline, start_time, end_time, duration, stops, price))


f.close()
