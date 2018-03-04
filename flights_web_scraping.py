from requests import get, post
from bs4 import BeautifulSoup as soup
from json import loads
from datetime import date, timedelta
import time
from urllib.parse import quote #used to url encode and replace characters with %xx escape


ONE_WAY_TRIP = '1'
RETURN_TRIP = '2'

FILE_NAME = 'flights.csv'

###############################################################################

flight_type = ''
start = ''
end = ''
date_1 = ''
date_2 = ''

# Open CSV file to be used when writing all results
f = open(FILE_NAME, 'w')

###############################################################################

def is_return_trip():
	return flight_type == RETURN_TRIP


def validate_airport(airport_code):
	""" Use OpenFlights website to authenticate airport codes

	Note:
		Only major/well-known airport codes will be authenticated
		Python script is to be used for planning routes between relatively known airports
	
	Args:
        airport_code (str): the 3 digit IATA code to be validated

    Returns:
        bool: True for valid (found) airport code, False if invalid

	"""

	# All airport codes are exactly 3 digits
	if len(airport_code) != 3:
		return False
		
	url = 'https://openflights.org/php/apsearch.php'
	
	params = {
		'name' : '', 
		'iata': airport_code.upper(),
		'icao': '',
		'city': '',
		'country': 'ALL',
		'code': '',
		'x': '',
		'y': '',
		'elevation': '',
		'timezone': '',
		'dst': 'U',
		'db': 'airports',
		'iatafilter': 'true',
		'apid': '',
		'action': 'SEARCH',
		'offset': '0'
	}
	
	response = post(url, data = params)
	response_json = loads(response.text)
	
	# No airports matching the 3-digit airport code found
	if len(response_json['airports']) < 1:
		return False
	
	return True

	
def validate_date(input_date):
	""" Validates any given date
	
	Args:
		input_date (str): date to be validated

	Returns:
		bool: True for valid date format and a date that lies between
			  tomorrow and 6 months from now
	
	"""

	if len(input_date) != 10:
		return False
	
	try:
		test_date = int(input_date[0:2])
		test_month = int(input_date[3:5])
		test_year = int(input_date[6:10])
	except ValueError:
		return False
		
	today = date.today()
	test_date = date(test_year, test_month, test_date)
	
	days_difference = test_date - today
		
	if test_date < today or days_difference.days > 185:
		return False
		
	return True

	
def validate_end_date(start_date, end_date):
	""" Validates End Date of Journey Chosen
	
	Completes a comparison check against start_date
	End date is also not to be chosen greater than 6 months in advance

	Args:
		start_date (str): a start date for the journey, presumably already validated
		end_date (str): an ending date for journey, to be validated

	Returns:
		bool: True for valid date format for end_date, and a date that lies between
			  tomorrow and 6 months from now, also expected to be on or after start_date
	
	"""

	if not validate_date(end_date):
		return False
		
	try:
		start = date(int(start_date[6:10]), int(start_date[3:5]), int(start_date[0:2]))
		end = date(int(end_date[6:10]), int(end_date[3:5]), int(end_date[0:2]))
	except ValueError:
		return False
	
	if end <= start:
		return False
		
	return True
	
	
def get_user_input():
	""" Get user input from command line
	
	Also validates each user input using appropriate helper functions
	Re-asks user for data if input validation fails
	
	"""

	flight_input = input('What type of flight is this:\n\t(1) One Way\n\t(2) Return Trip\n ')

	while flight_input != ONE_WAY_TRIP and flight_input != RETURN_TRIP:
		flight_input = input('Invalid input, enter either 1 or 2\n ')
		
	global flight_type
	flight_type = flight_input

	start_input = input('Enter the 3 digit airport code of the starting location: ')
	while not validate_airport(start_input):
		start_input = input('Invalid airport code entered, try again: ')
	
	global start
	start = start_input
	
	end_input = input('Enter the 3 digit airport code of the ending location: ')
	while not validate_airport(end_input):
		end_input = input('Invalid airport code entered, try again: ')

	global end
	end = end_input
		
	date_1_input = input('Enter the start date of the journey - DD/MM/YYYY: ')
	while not validate_date(date_1_input):
		date_1_input = input('Invalid date entered, try again: ')
	
	global date_1
	date_1 = date_1_input
	
	# Only ask user input for a second date if a return trip is chosen
	if is_return_trip():
		date_2_input = input('Enter the end date of the journey - DD/MM/YYYY: ')
		
		while not validate_end_date(date_1_input, date_2_input):
			date_2_input = input('Invalid date entered, try again: ')
		
		global date_2
		date_2 = date_2_input
	
	
def build_expedia_url():
	""" Build a url used to GET expedia results

	Returns:
		str: url-encoded string used to get a response from Expedia

	"""

	url = 'https://www.expedia.ca/Flights-Search'
	
	trip_type = '?trip=roundtrip' if is_return_trip() else '?trip=oneway'

	url += '{0}&leg1=from%3A{1}%2Cto%3A{2}%2Cdeparture%3A{3}%2F{4}%2F{5}TANYT'.format(
		trip_type, start, end, date_1[0:2], date_1[3:5], date_1[6:10]
	)

	if is_return_trip():
		url += '&leg2=from%3A{0}%2Cto%3A{1}%2C'.format(end, start)
		url += 'departure%3A{0}%2F{1}%2F{2}TANYT'.format(date_2[0:2], date_2[3:5], date_2[6:10])

	url += '&passengers=adults%3A1&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca'
	
	return url
	

def build_kiwi_url():
	""" Build a url used to GET Kiwi results

	Returns:
		str: url-encoded string used to get a response from Kiwi

	"""

	url = 'https://api.skypicker.com/flights?adults=1&asc=1'

	url += '&flyFrom={0}&to={1}&sort=price&dateFrom={2}%2F{3}%2F{4}&dateTo={2}%2F{3}%2F{4}'.format(
		start.upper(), end.upper(), date_1[0:2], date_1[3:5], date_1[6:10]
	)

	if is_return_trip():
		url += '&returnFrom={0}%2F{1}%2F{2}&returnTo={0}%2F{1}%2F{2}&typeFlight=return'.format(
			date_2[0:2], date_2[3:5], date_2[6:10]
		)
	else:
		url += '&typeFlight=oneway'
	
	return url


def get_exchange_rate(initial_currency):
	""" Get currency exchange rate from initial currency to CAD

	Use an online API to get hourly updated currency exchange rates

	Args:
		initial_currency (str): currency wanting to exhcange with CAD

	Returns:
		float: an exchange rate representing how much 1 unit of initial currency represents CAD
			   ex. if 1 USD = 1.321 CAD  then function returns 1.321

	"""

	# Account for condition that flight results were returned in CAD
	if initial_currency.upper() == 'CAD':
		return 1

	conversion = '{}_CAD'.format(initial_currency.upper())

	url = 'http://free.currencyconverterapi.com/api/v5/convert?q={0}&compact=y'.format(
		conversion
	)

	try:
		response = get(url)
		response_json = loads(response.text)
	except Exception:
		return 1

	rate = response_json[conversion]['val']

	return rate


def num_stops_to_text(stops):
	""" Convert numeric/string stop number to descriptive and consistent text 

	Args:
		stops (int/str): Number of stops

	Returns:
		str: String text depending on number of stops

	"""

	if type(stops) is str:
		try:
			stops = int(stops)
		except ValueError:
			return ''

	if stops < 0:
		return ''

	if stops == 0:
		return 'Nonstop'
	elif stops == 1:
		return '{0} Stop'.format(stops)

	return '{0} Stops'.format(stops)


def parse_html_for_info(html_parent, html_type, other):
	""" Parse html bs4 object for particular flight to find specific information 

	Look for next available element within html_parent, return stripped text from html element

	Args:
		html_parent (bs4.element.Tag): a specific flight result html element as a BeautifulSoup obj
		html_type (str): the type of html_element looking for (ex. span, div)
		other (dict): specifiying unique identifiers about html element like class

	Returns:
		str: the resulting information of an empty string if unsuccessful

	"""

	html_element = html_parent.find(html_type, other)
	if html_element is None:
		return ''
	
	return html_element.text.strip()


def airline_code_to_name(airline_code):
	""" Converts an airline's code to name using a lookup API

	Args:
		airline_code (str): the two-digit IATA airline code

	Returns:
		str: official airline name looked up using IATA code

	"""

	params = {
		'name': '',
		'alias': '',
		'iata': airline_code,
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

	url = 'https://openflights.org/php/alsearch.php'	

	response = post(url, data = params)
	new_line_index = response.text.find('\n')

	response_json = loads(response.text[new_line_index + 1:])

	if not 'name' in response_json:
		return ''

	return response_json['name']
	

def get_kayak_response():
	""" Obtains Kayak flight information for given route and date

	Utilizes cookies from home page in order to access flight information

	Returns
		requests.models.Response: A request reponse from Kayak's website

	"""

	home_url = 'https://www.kayak.com'
	home_response = get(home_url)
	kayak_cookies = home_response.cookies

	search_url = home_url + '/s/horizon/flights/results/FlightSearchPoll'

	kayak_date_1 = '{0}-{1}-{2}'.format(date_1[6:10], date_1[3:5], date_1[0:2])

	kayak_url_to_append = 'flights/{0}-{1}/{2}'.format(start.upper(), end.upper(), kayak_date_1)

	kayak_date_2 = ''
	if is_return_trip():
		kayak_date_2 = '{0}-{1}-{2}'.format(date_2[6:10], date_2[3:5], date_2[0:2])
		kayak_url_to_append += '/' + kayak_date_2

	referer = home_url + '/' + kayak_url_to_append

	headers = {
	    'Accept': '*/*',
	    'Accept-Language': 'en-US,en;q=0.9',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'Host': 'www.kayak.com',
	    'Referer': referer,
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	    'X-Requested-With': 'XMLHttpRequest'
	}

	oneway = str(not is_return_trip()).lower()

	params = {
	    'depart_date':kayak_date_1,
	    'return_date':kayak_date_2,
	    'oneway':oneway,
	    'origin_code':start.upper(),
	    'origincode':start.upper(),
	    'origin':start.upper(),
	    'destination':end.upper(),
	    'destination_code':end.upper(),
	    'depart_date_canon':kayak_date_1,
	    'return_date_canon':kayak_date_2,
	    'url':kayak_url_to_append,
	    'searchId':'',
	    'poll':'true',
	    'pollNumber':'0',
	    'applyFilters':'true',
	    'filterState':'',
	    'useViewStateFilterState':'false',
	    'pageNumber':'1',
	    'append':'false',
	    'pollingId':'593601',
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
	    'origin_location':'',
	    'nearby_origin':'false',
	    'destination_location':'',
	    'nearby_destination':'false',
	    'countrySearch':'false',
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
	    'id':'',
	    'navigateToResults':'false',
	    'ajaxts':'',
	    'scriptsMetadata':'',
	    'stylesMetadata':'',
	}

	response = post(search_url, headers = headers, data = params, cookies = kayak_cookies)

	return response
	

def get_flightnetwork_referer_url():
	""" Inputs appropriate data into dict, to be used in API call for query parameter
	
	String concatenation used to avoid python KeyError when filling up flight_legs variable

	Returns:
		str: a referer search url used for query parameters in flightnetwork web scraping

	"""

	flight_legs = '[{"date":"{' + date_1[6:10] + '-' + date_1[3:5] + '-' + date_1[0:2]
	flight_legs += '","destination":"' + end.upper() + '","origin":"' + start.upper() + '"}]'

	if is_return_trip():
		flight_legs = flight_legs[0:-1] + ',{"date":"{' + date_2[6:10] + '-' + date_2[3:5] + '-' + date_2[0:2]
		flight_legs += '","destination":"' + start.upper() + '","origin":"' + end.upper() + '"}]'

	trip_type = 'roundTrip' if is_return_trip() else 'oneway'
		
	referer_search = '{\
		"tripType":"' + trip_type + '",\
		"cabinClass":"economy",\
		"stopsFilter":[],\
		"legs":' + flight_legs + ',\
		"passengers":{"adults":1,"children":0,"infants":0},\
		"currency":{"code":"CAD"}\
	}'

	return referer_search.replace('\t', '')


def get_flightnetwork_response(url, url_header, home_cookies):
	referer_search = get_flightnetwork_referer_url()

	referer = url + 'en-CA/search?filter=' + quote(referer_search)

	search = referer_search[0:-1] + ',"references":{"source":"FN","client":"flightnetwork"},"flexFares":true}' 

	search_url = home_url + 'en-CA/api/flights/search/async?filter=' + quote(search)
	search_resp = get(search_url, headers = url_header, cookies = home_cookies)
	resp_json = loads(search_resp.text)

	i = 0

	while 'errors' in resp_json:
		i += 1
		search_resp = get(search_url, headers = url_header, cookies = home_cookies)
		resp_json = loads(search_resp.text)
		
		# allow for 5 attempts of retrying GET request
		if i >= 5:
			raise ValueError()

	return resp_json


def get_flightnetwork_itineraries():
	home_url = 'https://www.flightnetwork.com/'
	home_response = get(home_url)
	home_cookies = home_response.cookies

	header = {
		'Accept': '*/*',
	    'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br',
		'Host': 'www.flightnetwork.com',
		'Referer': home_url,
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	}			

	search_json = get_flightnetwork_response(home_url, header, home_cookies)

	header['Referer'] = referer
	header['Connection'] = 'keep-alive'

	url3 = 'https://www.flightnetwork.com/en-CA/api/flights/results/async?sid={0}&limit=0&t={1}'.format(
		search_json['id'], round(time.time()*1000)
	)

	response = get(url3, headers = header, cookies = home_cookies)
	response_json = loads(response.text)

	i = 0

	while response_json['status'] == 'InProgress' :

		# take a 2 second delay, try and see if backend querying is complete
		time.sleep(2)
		i += 1

		response = get(url3, headers = header, cookies = home_cookies)
		response_json = loads(response.text)
		
		# limit re-querying to 5 times (around 14+ sec delay)
		# also break if over 100 results found already
		if i >= 5 or len(response_json['itineraries']) > 100:
			break
		
	# remove excess journeys from reponse, only take top 100
	return response_json['itineraries'][0:100]


def parse_flightcentre_airlines(resp_soup, key_dict):
	""" Parses Beautiful response for flight key -> name mapping

	Args:
		airline_code (bs4.BeautifulSoup): Beautiful Soup response
		key_dict (dict): Dict containing the key (IATA airline code) -> values (name)

	"""

	header = resp_soup.find_all('div', {'class': 'flightFilterHeader'}, string='Airlines')
	labels = []

	if len(header) > 0:
		airline_filter_legend = header[0].find_next_sibling('div')
		labels = airline_filter_legend.find_all('label') 
	
	for label in labels:
		key_dict[label.input['value']] = label.text.strip()



###############################################################################
# MAIN
	
get_user_input()


# Write CSV Headers to file

csv_headers = 'Website,Airline,Start({0}),End({1}),Duration,Stops,'.format(
	start.upper(), end.upper()
)

if is_return_trip():
	csv_headers += 'Airline,Start ({0}),End({1}),Duration,Stops,'.format(
		end.upper(), start.upper()
	)

csv_headers += 'Price\n\n'

f.write(csv_headers)


# Web scraping from Expedia

expedia_url = build_expedia_url()
expedia_response = get(expedia_url)

expedia_soup = soup(expedia_response.text, 'html.parser')

continued_results_divs = expedia_soup.find_all('div', {'id': 'originalContinuationId'})

if len(continued_results_divs) > 0:
	expedia_results_id = continued_results_divs[0].text.strip()
	expedia_results_url = 'https://www.expedia.ca/Flight-Search-Paging?c={0}&is=1&sp=asc&cz=200&cn=0&ul=0'.format(
		expedia_results_id
	)
	
	expedia_results_response = get(expedia_results_url)
	expedia_json = loads(expedia_results_response.text)
	
	flights = expedia_json['content']['legs']
	flight_keys = list(flights)
	
	# send another Expedia request to gather second leg journeys
	if is_return_trip():
		expedia_results_2_url = expedia_results_url.replace(
			'is=1',
			'is=0&fl0=' + flight_keys[0]
		)
		
		expedia_results_2_url = expedia_results_2_url.replace('ul=0', 'ul=1')
		
		expedia_results_2_response = get(expedia_results_2_url)
		expedia_2_json = loads(expedia_results_2_response.text)
		
		flights_2 = expedia_2_json['content']['legs']
		
		flights = sorted(flights.items(), key=lambda x: x[1]['price']['exactPrice'])
		flights_2 = sorted(flights_2.items(), key=lambda x: x[1]['price']['exactPrice'])
		
		# Limit 10 flights to each journey leg, can create 10x10 = 100 combinations of journeys 
		flights = flights[:10]
		flights_2 = flights_2[:10]
		
		cheapest_first_leg_flight = flights[0][1]['price']['exactPrice']
		
		for flight in flights:
			start_time = flight[1]['departureTime']['time']
			end_time = flight[1]['arrivalTime']['time']
			
			duration = str(flight[1]['duration']['hours']) + 'h ' + str(flight[1]['duration']['minutes']) + 'm'
			price = flight[1]['price']['formattedPrice'][0:2] + flight[1]['price']['totalPriceAsDecimalString']
			
			airline = flight[1]['carrierSummary']['airlineName']
			if airline == '':
				airline = 'Multiple Airlines'
			
			stops = num_stops_to_text(flight[1]['formattedStops'])
			
			for flight_2 in flights_2:
				start_time_2 = flight_2[1]['departureTime']['time']
				end_time_2 = flight_2[1]['arrivalTime']['time']
			
				duration_2 = str(flight_2[1]['duration']['hours']) + 'h ' + str(flight_2[1]['duration']['minutes']) + 'm'
				
				airline_2 = flight_2[1]['carrierSummary']['airlineName']
				if airline_2 == '':
					airline_2 = 'Multiple Airlines'
				
				stops_2 = num_stops_to_text(flight_2[1]['formattedStops'])
				
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
			
			stops = num_stops_to_text(flights[key]['formattedStops'])

			f.write('Expedia,{0},{1},{2},{2},{4},{5}\n'.format(airline, start_time, end_time, duration, stops, price))
	
else:
	flights = expedia_soup.find_all('li', {'class': 'flight-module'})
	
	for flight in flights:

		start_time = parse_html_for_info(flight, 'span', {'data-test-id': 'departure-time'})
		end_time = parse_html_for_info(flight, 'span', {'data-test-id': 'arrival-time'})

		duration = parse_html_for_info(flight, 'span', {'data-test-id': 'duration'})
		airline = parse_html_for_info(flight, 'div', {'data-test-id': 'airline-name'})

		duration_span = flight.find('span', {'data-test-id': 'duration'})		
		stops_span = duration_span.find_next_sibling('span') 

		if stops_span is None or not stops_span.has_attr('data-test-num-stops'):
			stops = ''
		else:
			stops = stops_span.text.strip().replace('(', '').replace(')','')
		
		price_column_div = flight.find('div', {'data-test-id': 'price-column'})   
		if price_column_div is None:
			price = ''
		else:
			price_spans = price_column_div.div.findAll('span')
			if len(price_spans) == 0:
				price = ''
			else:
				price = price_spans[-1].text.strip().replace(',', '')
			
		f.write('Expedia,{0},{1},{2},{3},{4},{5}\n'.format(
			airline, start_time, end_time, duration, stops, price
		))


'''
	Web scraping from Kayak
'''

kayak_response = get_kayak_response()

kayak_json = loads(kayak_response.text)

kayak_soup = soup(kayak_json['content'], 'html.parser')

flights = kayak_soup.find_all('div', {'class': 'Flights-Results-FlightResultItem'}) 

for flight in flights:
	start_time_divs = flight.find_all('div', {'class': 'depart'})
	if len(start_time_divs) < 1:
		start_time = ''
	else:
		start_time = start_time_divs[0].div.text.strip().replace('\n', '')
		
	if is_return_trip():
		if len(start_time_divs) < 2:
			start_time_2 = ''
		else:
			start_time_2 = start_time_divs[1].div.text.strip().replace('\n', '')

	end_time_divs = flight.find_all('div', {'class': 'return'})
	if len(end_time_divs) < 1:
		end_time = ''
	else:
		end_time = end_time_divs[0].div.text.strip().replace('\n', '')
		
	if is_return_trip():
		if len(end_time_divs) < 2:
			end_time_2 = ''
		else:
			end_time_2 = end_time_divs[1].div.text.strip().replace('\n', '')
	
	duration_divs = flight.find_all('div', {'class': 'duration'})
	if len(duration_divs) < 1:
		duration = ''
	else:
		duration = duration_divs[0].div.text.strip().replace('\n', '')

	if is_return_trip():
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
			
	if is_return_trip():
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
		stops_inner_spans = stops_divs[0].find('span', {'class': 'axis'})
		if stops_inner_spans is None:
			stops = ''
		else:
			num_stops = len(stops_inner_spans.find_all('span', {'class': 'dot'}))
			stops = num_stops_to_text(num_stops)
	
	if is_return_trip():
		if len(stops_divs) < 2:
			stops_2 = ''
		else:
			stops_inner_spans_2 = stops_divs[0].find('span', {'class': 'axis'})
			if stops_inner_spans_2 is None:
				stops_2 = ''
			else:
				num_stops_2 = len(stops_inner_spans_2.find_all('span', {'class': 'dot'}))
				stops_2 = num_stops_to_text(num_stops_2)

	price = parse_html_for_info(flight, 'span', {'class': 'price'})

	f.write('Kayak,{0},{1},{2},{3},{4},'.format(airline, start_time, end_time, duration, stops))
	
	if is_return_trip():
		f.write('{0},{1},{2},{3},{4},'.format(
			airline_2, start_time_2, end_time_2, duration_2, stops_2
		))
		
	f.write('{0}\n'.format(price))


# Web scraping from FlightNetwork

flights = get_flightnetwork_itineraries()

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
	stops = num_stops_to_text(num_stops)
	
	price = flight['fare']['currency']['code'] + str(flight['fare']['total'])
	
	if is_return_trip():
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
		stops_2 = num_stops_to_text(num_stops_2)
		
	f.write('FlightNetwork,{0},{1},{2},{3},{4},'.format(
		airline, start_time, end_time, duration, stops
	))
	
	if is_return_trip():
		f.write('{0},{1},{2},{3},{4},'.format(
			airline_2, start_time_2, end_time_2, duration_2, stops_2
		))
		
	f.write('{0}\n'.format(price))
		

'''
	Web scraping from FlightCentre
'''

flightcenter_url = 'https://www.flightcentre.ca/flights/booking/outbound?time=&departure={0}&destination={1}'.format(
	start.upper(), end.upper()
)

departure_date = date_1[6:10] + date_1[3:5] + date_1[0:2]

if is_return_trip():
	return_date = date_2[6:10] + date_2[3:5] + date_2[0:2]
else:
	return_date = departure_date

flightcenter_url += '&departureDate={0}&returnDate={1}&seatClass=Y&adults=1&searchtype=RE'.format(
	departure_date, return_date, 'RE' if is_return_trip() else 'OW'
)

flightcenter_response = get(flightcenter_url)

flightcenter_soup = soup(flightcenter_response.text, 'html.parser')

flights = flightcenter_soup.find_all('div', {'class': 'outboundOffer'})

airline_keys = {}

parse_flightcentre_airlines(flightcenter_soup, airline_keys)
	

for flight in flights:
	bold_texts = flight.find_all('strong')
	
	start_time = bold_texts[8].text.strip()
	end_time = bold_texts[9].text.strip()
	
	duration = bold_texts[3].text.strip()
	stops = bold_texts[2].text.strip()
	price = bold_texts[4].text.strip()
	
	airline_key = flight.find('img')['alt']
	airline = airline_keys[airline_key]

	f.write('FlightCenter,{0},{1},{2},{3},{4},'.format(
		airline, start_time, end_time, duration, stops
	))
	
	if is_return_trip():
		form = flight.find('form')
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

		parse_flightcentre_airlines(flightcenter_soup_2, airline_keys)

		for flight_2 in flights_2:
			bold_texts_2 = flight_2.find_all('strong')
			
			start_time_2 = bold_texts_2[8].text.strip()
			end_time_2 = bold_texts_2[9].text.strip()
			
			duration_2 = bold_texts_2[3].text.strip()
			stops_2 = bold_texts_2[2].text.strip()
			price_2 = bold_texts_2[4].text.strip()
			
			airline_key_2 = flight_2.find('img')['alt']
			airline_2 = airline_keys[airline_key_2]
			
			f.write('{0},{1},{2},{3},{4},'.format(
				airline_2, start_time_2, end_time_2, duration_2, stops_2
			))

	f.write('{0}\n'.format(price))
		
'''
	Web scraping from Kiwi
'''

kiwi_url = build_kiwi_url()
kiwi_response = get(kiwi_url)

kiwi_response_json = loads(kiwi_response.text)

flights = kiwi_response_json['data']
currency = kiwi_response_json['currency']

exchange_rate = get_exchange_rate(currency)

for flight in flights:
	start_time_struct = time.gmtime(flight['dTime'])
	start_time = '{0}h {1}m'.format(start_time_struct.tm_hour, start_time_struct.tm_min)
	
	end_time_struct = time.gmtime(flight['aTime'])
	end_time = '{0}h {1}m'.format(end_time_struct.tm_hour, end_time_struct.tm_min)
	
	duration = flight['fly_duration']
	
	departure_flights = set([x['airline'] for x in flight['route'] if x['return'] == 0])
	return_flights = set([x['airline'] for x in flight['route'] if x['return'] == 1])
	
	stops = num_stops_to_text(len(departure_flights))
	
	if is_return_trip():
		return_flights_routes = [x for x in flight['route'] if x['return'] == 1]
		
		start_time_2_struct = time.gmtime(return_flights_routes[0]['dTime'])
		start_time_2 = '{0}h {1}m'.format(start_time_2_struct.tm_hour, start_time_2_struct.tm_min)
		
		end_time_2_struct = time.gmtime(return_flights_routes[-1]['aTime'])
		end_time_2 = '{0}h {1}m'.format(end_time_2_struct.tm_hour, end_time_2_struct.tm_min)
		
		duration_2 = flight['return_duration']
		stops_2 = num_stops_to_text(len(return_flights))

		airline = ( 'Multiple Airlines' if len(departure_flights) > 1 
					else airline_code_to_name(next(iter(departure_flights))) )

		airline_2 = ( 'Multiple Airlines' if len(return_flights) > 1 
					else airline_code_to_name(next(iter(return_flights))) )
				
	else:
		airline = ( 'Multiple Airlines' if len(departure_flights) > 1 
					else airline_code_to_name(next(iter(departure_flights))) )
	
	price_number = flight['price']*exchange_rate
	
	price = 'CAD$' + "{:.2f}".format(float(price_number))
	
	f.write('Kiwi,{0},{1},{2},{3},{4}'.format(airline, start_time, end_time, duration, stops))
	
	if is_return_trip():
		f.write(',{0},{1},{2},{3},{4}'.format(
			airline_2, start_time_2, end_time_2, duration_2, stops_2
		))
		
	f.write(',{0}\n'.format(price))
	

f.close()
