from requests import get, post, codes
from bs4 import BeautifulSoup as soup
from json import loads
from datetime import date, timedelta
import time
from urllib.parse import quote #used to url encode and replace characters with %xx escape


ONE_WAY_TRIP = '1'
RETURN_TRIP = '2'

SORT_BY_PRICE = 'p'
SORT_BY_DURATION = 'd'
SORT_BY_TIME = 't'

FILE_NAME = 'flights.csv'

###############################################################################

flight_type = ''
start = ''
end = ''
date_1 = ''
date_2 = ''
sort_type = ''

# Store all data found on websites into an array
csv_flights = []

###############################################################################

def is_return_trip():
	return flight_type == RETURN_TRIP


def validate_airport(airport_code):
	""" Use OpenFlights website to authenticate airport codes

	Only major/well-known airport codes can be authenticated
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
		'apid': '',
		'action': 'SEARCH',
		'city': '',
		'code': '',
		'country': 'ALL',
		'db': 'airports',
		'dst': 'U',
		'elevation': '',
		'iata': airport_code.upper(),
		'iatafilter': 'true',
		'icao': '',
		'name' : '', 
		'offset': '0',
		'timezone': '',
		'x': '',
		'y': ''
	}
	
	response = safe_post(url, params)
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
		
	# Do not allow date to be before today or beyond 6 months from today
	if test_date < today or days_difference.days > 185:
		return False
		
	return True

	
def validate_end_date(start_date, end_date):
	""" Validates End Date of Journey Chosen
	
	Complete a comparison check against start_date
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
	
	
def validate_sort_type(input_type):
	return input_type.lower() in {SORT_BY_PRICE, SORT_BY_DURATION, SORT_BY_TIME}


def get_user_input():
	""" Get user input from command line
	
	Validate each user input using appropriate helper functions
	Re-ask user for data if input validation fails
	
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

	print('How would you like the data formatted')
	sort_input = input(' p - Price, d = Duration, t = Start Time: ')
	while not validate_sort_type(sort_input):
		sort_input = input('Invalid sort type entered, enter p/d/t: ')

	global sort_type
	sort_type = sort_input.lower()
	

def safe_get(url, header = None, cookie = None):
	""" Send out GET request and handle exceptions from requests library

	Args:
		url (str): the URL to be requested and data received from
		header (dict): contains any request header parameters
		cookie (dict): contains any cookies required for requests to website

	Returns:
		requests.models.Response: URL Response

	"""

	try:
		response = get(url, headers = header, cookies = cookie)
	except Exception:
		print('Request not made, exited with an error for url:\n{0}'.format(url))
		exit()

	if response.status_code != codes.ok:
		print('Request resulted with an error status code for url:\n{0}'.format(url))
		exit()

	return response


def safe_post(url, params = None, header = None, cookie = None):
	""" Send out POST request and handle any resulting exceptions from requests library

	Args:
		url (str): the URL to be requested and data received from
		params (dict): any data to be sent with the POST request
		header (dict): contains any request header parameters
		cookie (dict): contains any cookies required for requests to website

	Returns:
		requests.models.Response: URL Response

	"""

	try:
		response = post(url, data = params, headers = header, cookies = cookie)
	except Exception:
		print('Request not made, exited with an error for url:\n{0}'.format(url))
		exit()

	if response.status_code != codes.ok:
		print('Request resulted with an error status code for url:\n{0}'.format(url))
		exit()

	return response

	
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


def parse_expedia_flight(flight):
	""" Parses an Expedia flight json reponse to obtain critical information

	Args:
		flight (dict): The JSON response obtained from request for a particular flight route

	Returns:
		dict: A dictionary containing the required information for an Expedia journey

	"""

	flight_object = {'website': 'Expedia'}
	flight_object['airline'] = flight['carrierSummary']['airlineName']
	
	# Empty airline name indicates multiple airlines for route
	if flight_object['airline'] == '':
		flight_object['airline'] = 'Multiple Airlines'

	flight_object['start_time'] = flight['departureTime']['time']
	flight_object['end_time'] = flight['arrivalTime']['time']
	
	flight_object['duration'] = str(flight['duration']['hours']) + 'h ' + str(flight['duration']['minutes']) + 'm'
	flight_object['stops'] = num_stops_to_text(flight['formattedStops'])

	return flight_object
	
	
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
		'action': 'SEARCH',
		'active': '',
		'alias': '',
		'alid': '',
		'callsign': '',
		'country': 'ALL',
		'iata': airline_code,
		'iatafilter': 'true',
		'icao': '',
		'mode': 'F',
		'name': '',
		'offset': '0'
	}

	url = 'https://openflights.org/php/alsearch.php'	

	response = safe_post(url, params)
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

	# Get cookies from home page to utilize in search request later
	home_url = 'https://www.kayak.com'
	home_response = safe_get(home_url)
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

	# Long list of paramaters used in the request
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
		'append':'false',
		'applyFilters':'true',
		'searchId':'',
		'poll':'true',
		'pollNumber':'0',
		'pollingId':'593601',
		'filterState':'',
		'pageNumber':'1',
		'useViewStateFilterState':'false',
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

	return safe_post(search_url, params, headers, kayak_cookies)
	

def parse_kayak_html(elements, required_count):
	""" Simple parsing for kayak elements, reduce duplicate code

	Args:
		elements (list): list of elements matching desired information
		required_count (int): require minimum number in the list for info to be parsed
	
	Returns:
		str: Stops in a text format

	"""

	if len(elements) < required_count:
		return ''
	else:
		return elements[required_count-1].div.text.strip().replace('\n', '')


def get_kayak_stops(stops_divs, count_needed):
	""" Overriding the previous method, specifically for stops, which require extra logic

	Args:
		elements (list): list of elements matching desired information
		required_count (int): require minimum number in the list for info to be parsed
	
	Returns:
		str: Stops in a text format

	"""


	if len(stops_divs) < count_needed:
		return ''
	else:
		stops_inner_spans = stops_divs[count_needed-1].find('span', {'class': 'axis'})
		if stops_inner_spans is None:
			return ''
		else:
			num_stops = len(stops_inner_spans.find_all('span', {'class': 'dot'}))
			return num_stops_to_text(num_stops)


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
		
	# One long string containing information tobe sent in URL
	referer_search = '{\
		"tripType":"' + trip_type + '",\
		"cabinClass":"economy",\
		"stopsFilter":[],\
		"legs":' + flight_legs + ',\
		"passengers":{"adults":1,"children":0,"infants":0},\
		"currency":{"code":"CAD"}\
	}'

	return referer_search.replace('\t', '')


def get_flightnetwork_response(url, url_header, home_cookies, referer_search):

	search = referer_search[0:-1] + ',"references":{"source":"FN","client":"flightnetwork"},"flexFares":true}' 

	search_url = url + 'en-CA/api/flights/search/async?filter=' + quote(search)
	search_resp = safe_get(search_url, url_header, home_cookies)
	resp_json = loads(search_resp.text)

	i = 0

	while 'errors' in resp_json:
		i += 1
		search_resp = safe_get(search_url, url_header, home_cookies)
		resp_json = loads(search_resp.text)
		
		# allow for 5 attempts of retrying GET request
		if i >= 5:
			print('Error in getting data from FlightNetwork')
			return None

	return resp_json


def get_flightnetwork_itineraries():
	""" Send requests and get flight itineraries from FlightNetwork

	Returns:
		list: The top 100 itineraries regarding one-way or return trips

	"""
	
	# Get cookies from homepage to use later in search request
	home_url = 'https://www.flightnetwork.com/'
	home_response = safe_get(home_url)
	home_cookies = home_response.cookies

	header = {
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br',
		'Host': 'www.flightnetwork.com',
		'Referer': home_url,
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	}			

	referer_search = get_flightnetwork_referer_url()

	search_json = get_flightnetwork_response(home_url, header, home_cookies, referer_search)
	if search_json is None:
		return []

	referer = home_url + 'en-CA/search?filter=' + quote(referer_search)

	header['Referer'] = referer
	header['Connection'] = 'keep-alive'

	url = 'https://www.flightnetwork.com/en-CA/api/flights/results/async?sid={0}&limit=0&t={1}'.format(
		search_json['id'], round(time.time()*1000)
	)

	response = safe_get(url, header, home_cookies)
	response_json = loads(response.text)

	i = 0

	while response_json['status'] == 'InProgress' :

		# take a 2 second delay, try and see if backend querying is complete
		time.sleep(2)
		i += 1

		response = safe_get(url, header, home_cookies)
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
		response = safe_get(url)
		response_json = loads(response.text)
	except Exception:
		return 1

	rate = response_json[conversion]['val']

	return rate
		

###############################################################################
# MAIN
	
get_user_input()

# Web scraping from Expedia

expedia_url = build_expedia_url()
expedia_response = safe_get(expedia_url)

expedia_soup = soup(expedia_response.text, 'html.parser')

continued_results_divs = expedia_soup.find_all('div', {'id': 'originalContinuationId'})

if len(continued_results_divs) > 0:
	expedia_results_id = continued_results_divs[0].text.strip()
	expedia_results_url = 'https://www.expedia.ca/Flight-Search-Paging?c={0}&is=1&sp=asc&cz=200&cn=0&ul=0'.format(
		expedia_results_id
	)
	
	expedia_results_response = safe_get(expedia_results_url)
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
		
		expedia_results_2_response = safe_get(expedia_results_2_url)
		
		expedia_2_json = loads(expedia_results_2_response.text)
		
		flights_2 = expedia_2_json['content']['legs']
		
		flights = sorted(flights.items(), key=lambda x: x[1]['price']['exactPrice'])
		flights_2 = sorted(flights_2.items(), key=lambda x: x[1]['price']['exactPrice'])
		
		# Limit 10 flights to each journey leg, can create 10x10 = 100 combinations of journeys 
		flights = flights[:10]
		flights_2 = flights_2[:10]
		
		# Prices for 2nd leg will be according to first flight picked from leg 1
		# For routes using a different flight for leg 1, the difference in costs will added
		cheapest_first_leg_flight = flights[0][1]['price']['exactPrice']
		
		for flight in flights:
			flight_obj = parse_expedia_flight(flight[1])

			for flight_2 in flights_2:
				flight_obj_2 = flight_obj.copy()

				flight_obj_2['airline_2'] = flight_2[1]['carrierSummary']['airlineName']
				if flight_obj_2['airline_2'] == '':
					flight_obj_2['airline_2'] = 'Multiple Airlines'
				
				flight_obj_2['start_time_2'] = flight_2[1]['departureTime']['time']
				flight_obj_2['end_time_2'] = flight_2[1]['arrivalTime']['time']
				
				flight_duration = flight_2[1]['duration'];
				flight_obj_2['duration_2'] = str(flight_duration['hours']) + 'h ' + str(flight_duration['minutes']) + 'm'
			
				flight_obj_2['stops_2'] = num_stops_to_text(flight_2[1]['formattedStops'])
				
				price_2 = flight_2[1]['price']['exactPrice'] + flight[1]['price']['exactPrice'] - cheapest_first_leg_flight
				flight_obj_2['price'] = "{:.2f}".format(float(price_2))

				csv_flights.append(flight_obj_2)
		
	else:
		for key in flights:
			flight_obj = parse_expedia_flight(flights[key])

			flight_obj['price'] = flights[key]['price']['totalPriceAsDecimalString']

			csv_flights.append(flight_obj)
	
else:
	flights = expedia_soup.find_all('li', {'class': 'flight-module'})
	
	for flight in flights:
		flight_obj = {'website': 'Expedia'}

		flight_obj['airline'] = parse_html_for_info(flight, 'div', {'data-test-id': 'airline-name'})
		flight_obj['start_time'] = parse_html_for_info(flight, 'span', {'data-test-id': 'departure-time'})
		flight_obj['end_time'] = parse_html_for_info(flight, 'span', {'data-test-id': 'arrival-time'})
		flight_obj['duration'] = parse_html_for_info(flight, 'span', {'data-test-id': 'duration'})

		duration_span = flight.find('span', {'data-test-id': 'duration'})		
		stops_span = duration_span.find_next_sibling('span') 

		if stops_span is None or not stops_span.has_attr('data-test-num-stops'):
			flight_obj['stops'] = ''
		else:
			flight_obj['stops'] = stops_span.text.strip().replace('(', '').replace(')','')
		
		price_column_div = flight.find('div', {'data-test-id': 'price-column'})   
		if price_column_div is None:
			flight_obj['price'] = ''
		else:
			price_spans = price_column_div.div.findAll('span')
			flight_obj['price'] = ( '' if len(price_spans) == 0
									else price_spans[-1].text.strip().replace(',', '') )

	csv_flights.append(flight_obj)


'''
	Web scraping from Kayak
'''

kayak_response = get_kayak_response()

kayak_json = loads(kayak_response.text)

kayak_soup = soup(kayak_json['content'], 'html.parser')

flights = kayak_soup.find_all('div', {'class': 'Flights-Results-FlightResultItem'}) 

for flight in flights:
	flight_obj = {'website': 'Kayak'}

	airline_divs = flight.find_all('div', {'class': 'carrier'})
	if len(airline_divs) < 1:
		flight_obj['airline'] = ''
	else:
		airline_inner_divs = airline_divs[0].find_all('div')
		flight_obj['airline'] = '' if len(airline_inner_divs) < 1 else airline_inner_divs[-1].text.strip()

	start_time_divs = flight.find_all('div', {'class': 'depart'})
	flight_obj['start_time'] = parse_kayak_html(start_time_divs, 1).replace(' ', '')

	end_time_divs = flight.find_all('div', {'class': 'return'})
	flight_obj['end_time'] = parse_kayak_html(end_time_divs, 1).replace(' ', '')

	duration_divs = flight.find_all('div', {'class': 'duration'})
	flight_obj['duration'] = parse_kayak_html(duration_divs, 1)

	stops_divs = flight.find_all('div', {'class': 'stops'})
	flight_obj['stops'] = get_kayak_stops(stops_divs, 1)
	
	if is_return_trip():
		if len(airline_divs) < 2:
			flight_obj['airline_2'] = ''
		else:
			airline_inner_divs_2 = airline_divs[1].find_all('div')
			flight_obj['airline_2'] = '' if len(airline_inner_divs_2) < 1 else airline_inner_divs_2[-1].text.strip()
		
		flight_obj['start_time_2'] = parse_kayak_html(start_time_divs, 2).replace(' ', '')
		flight_obj['end_time_2'] = parse_kayak_html(end_time_divs, 2).replace(' ', '')

		flight_obj['duration_2'] = parse_kayak_html(duration_divs, 2)
		flight_obj['stops_2'] = get_kayak_stops(stops_divs, 2)

	flight_obj['price'] = parse_html_for_info(flight, 'span', {'class': 'price'})[1:]
	csv_flights.append(flight_obj)


# Web scraping from FlightNetwork

flights = get_flightnetwork_itineraries()

for flight in flights:
	flight_obj = {'website': 'FlightNetwork'}
	
	segments = flight['legs'][0]['segments']
	one_airline = all(segment['marketing']['code'] == segments[0]['marketing']['code'] for segment in segments)
	
	flight_obj['airline'] = segments[0]['marketing']['name'] if one_airline else 'Multiple Airlines' 

	flight_obj['start_time'] = flight['legs'][0]['departureTime']
	flight_obj['end_time'] = flight['legs'][0]['arrivalTime']
	
	duration_time = flight['legs'][0]['duration']
	flight_obj['duration'] = '{0}h {1}m'.format(int(duration_time/60), duration_time%60)
	
	num_stops = len(segments) - 1
	flight_obj['stops'] = num_stops_to_text(num_stops)
	
	if is_return_trip():
		segments_2 = flight['legs'][1]['segments']
		one_airline_2 = all(segment_2['marketing']['code'] == segments_2[0]['marketing']['code'] for segment_2 in segments_2)
		
		flight_obj['airline_2'] = segments_2[0]['marketing']['name'] if one_airline_2 else 'Multiple Airlines' 

		flight_obj['start_time_2'] = flight['legs'][1]['departureTime']
		flight_obj['end_time_2'] = flight['legs'][1]['arrivalTime']

		duration_time_2 = flight['legs'][1]['duration']
		flight_obj['duration_2'] = '{0}h {1}m'.format(int(duration_time_2/60), duration_time_2%60)

		num_stops_2 = len(segments_2) - 1
		flight_obj['stops_2'] = num_stops_to_text(num_stops_2)
		
	flight_obj['price'] = str(flight['fare']['total'])

	csv_flights.append(flight_obj)
		

# Web scraping from FlightCentre

flightcenter_url = 'https://www.flightcentre.ca/flights/booking/outbound?time=&departure={0}&destination={1}'.format(
	start.upper(), end.upper()
)

departure_date = date_1[6:10] + date_1[3:5] + date_1[0:2]
return_date = departure_date if not is_return_trip() else  date_2[6:10] + date_2[3:5] + date_2[0:2]

flightcenter_url += '&departureDate={0}&returnDate={1}&seatClass=Y&adults=1&searchtype=RE'.format(
	departure_date, return_date, 'RE' if is_return_trip() else 'OW'
)

flightcenter_response = safe_get(flightcenter_url)

flightcenter_soup = soup(flightcenter_response.text, 'html.parser')

flights = flightcenter_soup.find_all('div', {'class': 'outboundOffer'})

airline_keys = {'Multiple Airlines': 'Multiple Airlines'}

parse_flightcentre_airlines(flightcenter_soup, airline_keys)

for flight in flights:
	flight_obj = {'website': 'FlightCentre'}

	airline_key = flight.find('img')['alt']
	flight_obj['airline'] = airline_keys[airline_key]
	
	bold_texts = flight.find_all('strong')

	flight_obj['start_time'] = bold_texts[8].text.strip().replace(' ', '').lower()
	flight_obj['end_time'] = bold_texts[9].text.strip().replace(' ', '').lower()
	
	flight_obj['duration'] = bold_texts[3].text.strip()
	flight_obj['stops'] = bold_texts[2].text.strip()
	
	# Return journeys will need another API request to get details
	if is_return_trip():
		
		# find a hidden form within the webpage
		form = flight.find('form')
		inputs = form.find_all('input')
		
		# Form and inputs collected above to be sent to return left API request
		flightcenter_url_2 = 'https://www.flightcentre.ca/flights/booking/inbound'
		
		params = {}
		
		# Grab form inputs from hidden form for request to be sent later
		for input in inputs:
			params[input['name']] = input['value']
		
		flightcenter_response_2 = safe_post(flightcenter_url_2, params)
		
		flightcenter_soup_2 = soup(flightcenter_response_2.text, 'html.parser')

		flights_2 = flightcenter_soup_2.find_all('div', {'class': 'outboundOffer'})
		
		# ignore the first one, which is the chosen departure flight
		flights_2 = flights_2[1:]

		parse_flightcentre_airlines(flightcenter_soup_2, airline_keys)

		for flight_2 in flights_2:
			airline_key_2 = flight_2.find('img')['alt']
			flight_obj['airline_2'] = airline_keys[airline_key_2]

			bold_texts_2 = flight_2.find_all('strong')
			
			flight_obj['start_time_2'] = bold_texts_2[8].text.strip().replace(' ', '').lower()
			flight_obj['end_time_2'] = bold_texts_2[9].text.strip().replace(' ', '').lower()
			
			flight_obj['duration_2'] = bold_texts_2[3].text.strip()
			flight_obj['stops_2'] = bold_texts_2[2].text.strip()
			
	flight_obj['price'] = ( bold_texts[4].text.replace('$', '').strip() if not is_return_trip()
							else bold_texts_2[4].text.replace('$', '').strip() )

	csv_flights.append(flight_obj)


# Web scraping from Kiwi

kiwi_url = build_kiwi_url()
kiwi_response = safe_get(kiwi_url)

kiwi_response_json = loads(kiwi_response.text)

flights = kiwi_response_json['data']

# Kiwi does not always use CAD, obtain currency exchange information
currency = kiwi_response_json['currency']
exchange_rate = get_exchange_rate(currency)

for flight in flights:
	flight_obj = {'website': 'Kiwi'}

	start_time_struct = time.gmtime(flight['dTime'])
	flight_obj['start_time'] = time.strftime("%I:%M%p", start_time_struct).lower()

	end_time_struct = time.gmtime(flight['aTime'])
	flight_obj['end_time'] = time.strftime("%I:%M%p", end_time_struct).lower()
	
	flight_obj['duration'] = flight['fly_duration']
	
	departure_flights = set([x['airline'] for x in flight['route'] if x['return'] == 0])

	flight_obj['airline'] = ( 'Multiple Airlines' if len(departure_flights) > 1 
					else airline_code_to_name(next(iter(departure_flights))) )
	
	flight_obj['stops'] = num_stops_to_text(len(departure_flights))
	
	if is_return_trip():
		return_flights_routes = [x for x in flight['route'] if x['return'] == 1]

		return_flights = set([x['airline'] for x in flight['route'] if x['return'] == 1])
		flight_obj['airline_2'] = ( 'Multiple Airlines' if len(return_flights) > 1 
					else airline_code_to_name(next(iter(return_flights))) )
		
		start_time_2_struct = time.gmtime(return_flights_routes[0]['dTime'])
		flight_obj['start_time_2'] = time.strftime("%I:%M%p", start_time_2_struct).lower()
		
		end_time_2_struct = time.gmtime(return_flights_routes[-1]['aTime'])
		flight_obj['end_time_2'] = time.strftime("%I:%M%p", end_time_2_struct.tm_min).lower()
		
		flight_obj['duration_2'] = flight['return_duration']
		flight_obj['stops_2'] = num_stops_to_text(len(return_flights))
	
	price_number = flight['price']*exchange_rate
	flight_obj['price'] = "{:.2f}".format(float(price_number))
	
	csv_flights.append(flight_obj)


# Open CSV file to be used when writing all results
f = open(FILE_NAME, 'w')

# Write CSV Headers to file
csv_headers = 'Website,Airline,Start({0}),End({1}),Duration,Stops,'.format(
	start.upper(), end.upper()
)

if is_return_trip():
	csv_headers += 'Airline,Start ({0}),End({1}),Duration,Stops,'.format(
		end.upper(), start.upper()
	)

csv_headers += 'Price(CAD)\n\n'

f.write(csv_headers)

if sort_type == SORT_BY_PRICE:
	csv_flights.sort(key = lambda x: float(x['price']))
elif sort_type == SORT_BY_TIME:
	try:
		csv_flights.sort(key = lambda x : time.strptime(x['start_time'], "%I:%M%p")) 
	except:
		print("Unable to sort according to start time due to string format")
elif sort_type == SORT_BY_DURATION:
	csv_flights.sort(key = lambda x: timedelta(hours = int(x['duration'][0:x['duration'].find('h')]), minutes = int(x['duration'][-3:-1])))

# Sample flight keys from first flight, all flight objects should have same keys
flight_keys = list(csv_flights[0].keys())

for flight in csv_flights:
	flight_string = ''
	for flight_key in flight_keys:
		flight_string += str(flight[flight_key]) + ','
	f.write(flight_string[:-1] + '\n')

f.close()
