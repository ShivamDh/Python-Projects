from requests import get, post
from bs4 import BeautifulSoup as soup
import json
import time
from urllib.parse import quote

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
		
	if flight_type == '2':
		if len(start_time_divs) < 2:
			start_time_2 = ''
		else:
			start_time_2 = start_time_divs[1].div.text.strip().replace('\n', '')

	end_time_divs = flight.find_all('div', {'class': 'return'})
	if len(end_time_divs) < 1:
		end_time = ''
	else:
		end_time = end_time_divs[0].div.text.strip().replace('\n', '')
		
	if flight_type == '2':
		if len(end_time_divs) < 2:
			end_time_2 = ''
		else:
			end_time_2 = end_time_divs[1].div.text.strip().replace('\n', '')
	
	duration_divs = flight.find_all('div', {'class': 'duration'})
	if len(duration_divs) < 1:
		duration = ''
	else:
		duration = duration_divs[0].div.text.strip().replace('\n', '')

	if flight_type == '2':
		if len(duration_divs) < 2:
			duration_2 = ''
		else:
			duration_2 = duration_divs[1].div.text.strip().replace('\n', '')
		
	airline_divs = flight.find_all('div', {'class': 'carrier'})
	if len(airline_divs) < 1:
		airline = ''
	else:
		airline_inner_divs = airline_divs[0].find_all('div')
		if len(airline_inner_divs) > 0:
			airline = airline_inner_divs[-1].text.strip()
		else:
			airline = ''
			
	if flight_type == '2':
		if len(airline_divs) < 2:
			airline_2 = ''
		else:
			airline_inner_divs_2 = airline_divs[1].find_all('div')
			if len(airline_inner_divs_2) > 0:
				airline_2 = airline_inner_divs_2[-1].text.strip()
			else:
				airline_2 = ''
			
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
	
	if flight_type == '2':
		if len(stops_divs) < 2:
			stops_2 = ''
		else:
			stops_inner_spans_2 = stops_divs[0].find_next('span', {'class': 'axis'})
			if stops_inner_spans_2 is None:
				stops_2 = ''
			else:
				num_stops_2 = len(stops_inner_spans_2.find_all('span', {'class': 'dot'}))
				if num_stops_2 == 0:
					stops_2 = 'Nonstop'
				elif num_stops == 1:
					stops_2 = '1 stop'
				else:
					stops_2 = '{0} stops'.format(len(num_stops))

	price_spans = flight.find_next('span', {'class': 'price'})
	if price_spans is None:
		price = ''
	else:
		price = price_spans.text.strip()

	f.write('Kayak,{0},{1},{2},{3},{4}'.format(airline, start_time, end_time, duration, stops))
	
	if flight_type == '2':
		f.write(',{0},{1},{2},{3},{4}'.format(airline_2, start_time_2, end_time_2, duration_2, stops_2))
		
	f.write(',{0}\n'.format(price))


'''
	Web scraping from FlightNetwork
'''

flightnetwork_home_url = 'https://www.flightnetwork.com/'
flightnetwork_response = get(flightnetwork_home_url)
flightnetwork_cookies = flightnetwork_response.cookies

header = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	'Referer': flightnetwork_home_url,
	'Host': 'www.flightnetwork.com',
	'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
	'Accept-Encoding': 'gzip, deflate, br'
}

flight_legs = '[{"date":"{'+date_1[6:10]+'-'+date_1[3:5]+'-'+date_1[0:2]+'","destination":"'+end.upper()+'","origin":"'+start.upper()+'"}]'

if flight_type == '2':
	flight_legs = flight_legs[0:-1] + ',{"date":"{' + date_2[6:10] + '-' + date_2[3:5] + '-' + date_2[0:2] + '",'
	flight_legs += '"destination":"' + start.upper() + '","origin":"' + end.upper() + '"}]'

referer_search = '{\
	"tripType":"oneway",\
	"cabinClass":"economy",\
	"stopsFilter":[],\
	"legs":' + flight_legs + ',\
	"passengers":{"adults":1,"children":0,"infants":0},\
	"currency":{"code":"CAD"}\
}'

referer_search = referer_search.replace('\t', '')

referer = flightnetwork_home_url + 'en-CA/search?filter=' + quote(referer_search)

flightnetwork_search = referer_search[0:-1] + ',"references":{"source":"FN","client":"flightnetwork"},"flexFares":true}' 

flightnetwork_search_url = flightnetwork_home_url + 'en-CA/api/flights/search/async?filter=' + quote(flightnetwork_search)
flightnetwork_search_resp = get(flightnetwork_search_url, headers = header, cookies=flightnetwork_cookies)
flightnetwork_search_resp_json = json.loads(flightnetwork_search_resp.text)

i = 0

while 'errors' in flightnetwork_search_resp_json:
	i += 1
	flightnetwork_search_resp = get(flightnetwork_search_url, headers = header, cookies=flightnetwork_cookies)
	flightnetwork_search_resp_json = json.loads(flightnetwork_search_resp.text)
	
	if i >= 5:
		f.close()
		exit()
		
header2 = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	'Referer': referer,
	'Host': 'www.flightnetwork.com',
	'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
	'Accept-Encoding': 'gzip, deflate, br',
	'Connection': 'keep-alive'
}

url3 = 'https://www.flightnetwork.com/en-CA/api/flights/results/async?sid={0}&limit=0&t={1}'.format(
	flightnetwork_search_resp_json['id'],
	round(time.time()*1000)
)

resp2 = get(url3, headers = header2, cookies = flightnetwork_cookies)
resp2_json = json.loads(resp2.text)

i = 0

while resp2_json['status'] == 'InProgress' :
	time.sleep(2)
	i += 1
	resp2 = get(url3, headers = header2, cookies = flightnetwork_cookies)
	resp2_json = json.loads(resp2.text)
	
	# limit re-querying to 7 times (around 14+ sec delay)
	# also break if over 100 results found already
	if i >= 7 or len(resp2_json['itineraries']) > 100:
		break
		
flights = resp2_json['itineraries'][0:100]

for flight in flights:
	start_time = flight['legs'][0]['departureTime']
	end_time = flight['legs'][0]['arrivalTime']
	
	duration_time = flight['legs'][0]['duration']
	duration = '{0}h {1}m'.format(int(duration_time/60), duration_time%60)
	
	segments = flight['legs'][0]['segments']
	one_airline = all(segment['marketing']['code'] == segments[0]['marketing']['code'] for segment in segments)
	
	if one_airline:
		airline = segments[0]['marketing']['name']
	else:
		airline = 'Multiple Airlines'
	
	num_stops = len(segments) - 1
	if num_stops == 0:
		stops = 'Nonstop'
	elif num_stops == 1:
		stops = '1 stop'
	else:
		stops = '{0} stops'.format(num_stops)
	
	price = flight['fare']['currency']['code'] + str(flight['fare']['total'])
	
	if flight_type == '2':
		start_time_2 = flight['legs'][1]['departureTime']
		end_time_2 = flight['legs'][1]['arrivalTime']

		duration_time_2 = flight['legs'][1]['duration']
		duration_2 = '{0}h {1}m'.format(int(duration_time_2/60), duration_time_2%60)
		
		segments_2 = flight['legs'][1]['segments']
		one_airline_2 = all(segment_2['marketing']['code'] == segments_2[0]['marketing']['code'] for segment_2 in segments_2)
		
		if one_airline_2:
			airline_2 = segments_2[0]['marketing']['name']
		else:
			airline_2 = 'Multiple Airlines'
			
		num_stops_2 = len(segments_2) - 1
		if num_stops_2 == 0:
			stops_2 = 'Nonstop'
		elif num_stops_2 == 1:
			stops_2 = '1 stop'
		else:
			stops_2 = '{0} stops'.format(num_stops_2)
		
	f.write('FlightNetwork,{0},{1},{2},{3},{4}'.format(airline, start_time, end_time, duration, stops))
	
	if flight_type == '2':
		f.write(',{0},{1},{2},{3},{4}'.format(airline_2, start_time_2, end_time_2, duration_2, stops_2))
		
	f.write(',{0}\n'.format(price))
		

'''
	Web scraping from FlightCentre'
'''

flightcenter_url = 'https://www.flightcentre.ca/flights/booking/outbound?time=&departure={0}&destination={1}'.format(
	start.upper(), end.upper()
)

departure_date = date_1[6:10] + date_1[3:5] + date_1[0:2]

if flight_type == '2':
	return_date = date_2[6:10] + date_2[3:5] + date_2[0:2]
else:
	return_date = departure_date

flightcenter_url += '&departureDate={0}&returnDate={1}&seatClass=Y&adults=1&searchtype=RE'.format(
	departure_date, return_date, 'OW' if flight_type == '1' else 'RE'
)

flightcenter_response = get(flightcenter_url)

flightcenter_soup = soup(flightcenter_response.text, 'html.parser')

flights = flightcenter_soup.find_all('div', {'class': 'outboundOffer'})

airline_filter = flightcenter_soup.find_all('div', {'class': 'flightFilterHeader'}, string='Airlines')

airline_keys = {}

if len(airline_filter) > 0:
	airline_filter_legend = airline_filter[0].find_next_sibling('div')
	airline_labels = airline_filter_legend.find_all('label') 
	
	for label in airline_labels:
		airline_keys[label.input['value']] = label.text.strip()
	

for flight in flights:
	bold_texts = flight.find_all('strong')
	
	start_time = bold_texts[8].text.strip()
	end_time = bold_texts[9].text.strip()
	
	duration = bold_texts[3].text.strip()
	stops = bold_texts[2].text.strip()
	price = bold_texts[4].text.strip()
	
	airline_key = flight.find_next('img')['alt']
	airline = airline_keys[airline_key]
	
	if flight_type == '2':
		form = flight.find_next('form')
		inputs = form.find_all('input')
		flightcenter_url_2 = 'https://www.flightcentre.ca/flights/booking/inbound'
		
		params = {}
		
		for input in inputs:
			params[input['name']] = input['value']
		
		flightcenter_response_2 = post(flightcenter_url_2, data = params)
		
		flightcenter_soup_2 = soup(flightcenter_response_2.text, 'html.parser')

		flights_2 = flightcenter_soup_2.find_all('div', {'class': 'outboundOffer'})
		
		# ignore the first one, which is the chosen departure flight
		flights_2 = flights_2[1:]

		airline_filter_2 = flightcenter_soup.find_all('div', {'class': 'flightFilterHeader'}, string='Airlines')

		if len(airline_filter_2) > 0:
			airline_filter_legend_2 = airline_filter_2[0].find_next_sibling('div')
			airline_labels_2 = airline_filter_legend_2.find_all('label') 
			
			for label_2 in airline_labels_2:
				airline_keys[label_2.input['value']] = label_2.text.strip()
		
		for flight_2 in flights_2:
			bold_texts_2 = flight_2.find_all('strong')
			
			start_time_2 = bold_texts_2[8].text.strip()
			end_time_2 = bold_texts_2[9].text.strip()
			
			duration_2 = bold_texts_2[3].text.strip()
			stops_2 = bold_texts_2[2].text.strip()
			price_2 = bold_texts_2[4].text.strip()
			
			airline_key_2 = flight_2.find_next('img')['alt']
			airline_2 = airline_keys[airline_key_2]
			
			f.write('FlightCentre,{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(
				airline, start_time, end_time, duration, stops,
				airline_2, start_time_2, end_time_2, duration_2, stops_2,
				price
			))
		
'''
	Web scraping from Kiwi
'''

kiwi_url = 'https://api.skypicker.com/flights?adults=1&asc=1&flyFrom={0}&to={1}&sort=price'.format(
	start.upper(), end.upper()
)

kiwi_url += '&dateFrom={0}%2F{1}%2F{2}&dateTo={0}%2F{1}%2F{2}'.format(
	date_1[0:2], date_1[3:5], date_1[6:10]
)

if flight_type == '1':
	kiwi_url += '&typeFlight=oneway'
else:
	kiwi_url += '&returnFrom={0}%2F{1}%2F{2}&returnTo={0}%2F{1}%2F{2}&typeFlight=return'.format(
		date_2[0:2], date_2[3:5], date_2[6:10]
	)

kiwi_response = get(kiwi_url)

kiwi_response_json = json.loads(kiwi_response.text)

flights = kiwi_response_json['data']
currency = kiwi_response_json['currency']

currency_conversion = '{}_CAD'.format(currency.upper())
currency_exchange_url = 'http://free.currencyconverterapi.com/api/v5/convert?q={0}&compact=y'.format(currency_conversion)

currency_exchange_response = get(currency_exchange_url)

currency_exchange_json = json.loads(currency_exchange_response.text)
exchange_rate = currency_exchange_json[currency_conversion]['val']

airline_code_search_params = {
	'name': '',
	'alias': '',
	'iata': '',
	'icao': '',
	'country': 'ALL',
	'callsign': '',
	'mode': 'F',
	'active': '',
	'offset': '0',
	'iatafilter': 'true',
	'alid': '',
	'action': 'SEARCH'
}

airline_code_search_url = 'https://openflights.org/php/alsearch.php'

for flight in flights:
	start_time_struct = time.gmtime(flight['dTime'])
	start_time = '{0}h {1}m'.format(start_time_struct.tm_hour, start_time_struct.tm_min)
	
	end_time_struct = time.gmtime(flight['aTime'])
	end_time = '{0}h {1}m'.format(end_time_struct.tm_hour, end_time_struct.tm_min)
	
	duration = flight['fly_duration']
	
	departure_flights = set([x['airline'] for x in flight['route'] if x['return'] == 0])
	departure_flights_len = len(departure_flights)
	
	return_flights = set([x['airline'] for x in flight['route'] if x['return'] == 1])
	return_flights_len = len(return_flights)
	
	if departure_flights_len == 0:
		stops = 'Nonstop'
	elif departure_flights_len == 1:
		stops = '1 stop'
	else:
		stops = '{0} stops'.format(departure_flights_len)
	
	
	if flight_type == '1':
		if len(flight['airlines']) > 1:
			airline = 'Multiple Airlines'
		else:
			airline_code_search_params['iata'] = flight['airlines'][0]
			
			airline_code_search_response = post(airline_code_search_url, data = airline_code_search_params)
			
			new_line = airline_code_search_response.text.find('\n')
			airline_code_json = json.loads(airline_code_search_response.text[new_line + 1:])
			
			airline = airline_code_json['name']
	
	else:
		return_flights_routes = [x for x in flight['route'] if x['return'] == 1]
		
		start_time_2_struct = time.gmtime(return_flights_routes[0]['dTime'])
		start_time_2 = '{0}h {1}m'.format(start_time_2_struct.tm_hour, start_time_2_struct.tm_min)
		
		end_time_2_struct = time.gmtime(return_flights_routes[-1]['aTime'])
		end_time_2 = '{0}h {1}m'.format(end_time_2_struct.tm_hour, end_time_2_struct.tm_min)
		
		duration_2 = flight['return_duration']
		
		if return_flights_len == 0:
			stops_2 = 'Nonstop'
		elif return_flights_len == 1:
			stops_2 = '1 stop'
		else:
			stops_2 = '{0} stops'.format(return_flights_len)
	
		
		if len(departure_flights) > 1:
			airline = 'Multiple Airlines'
		else:
			airline_code_search_params['iata'] = next(iter(departure_flights))
			
			airline_code_search_response = post(airline_code_search_url, data = airline_code_search_params)
			
			new_line = airline_code_search_response.text.find('\n')
			airline_code_json = json.loads(airline_code_search_response.text[new_line + 1:])
			
			airline = airline_code_json['name']
			
		if len(return_flights) > 1:
			airline_2 = 'Multiple Airlines'
		else:
			airline_code_search_params['iata'] = next(iter(departure_flights))
			
			airline_code_search_response = post(airline_code_search_url, data = airline_code_search_params)
			
			new_line = airline_code_search_response.text.find('\n')
			airline_code_json_2 = json.loads(airline_code_search_response.text[new_line + 1:])
			
			airline_2 = airline_code_json['name']

	
	price_number = flight['price']*exchange_rate
	
	price = 'CAD$' + "{:.2f}".format(float(price_number))
	
	f.write('Kiwi,{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(
		airline, start_time, end_time, duration, stops,
		airline_2, start_time_2, end_time_2, duration_2, stops_2,
		price
	))

	
	

f.close()
