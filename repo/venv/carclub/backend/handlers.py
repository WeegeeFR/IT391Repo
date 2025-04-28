import requests
from bs4 import BeautifulSoup
from datetime import datetime

#base url to results page
results_url = "https://ccsportscarclub.org/autocross/schedule/pastresults/2023-autocross-results/"
replace_list = ['FinalRawPax', 'RawPaxFinal', 'Grudges', 'Saturday', 'Sunday', 'finalrawpax']

#valid settings are 'Raw' and 'Pax'
def scrape_season_events():
    scraped_data = {}
    response = requests.get(results_url)
    if response.status_code != 200:
        raise Exception(f"Error fetching page {results_url}, status code: {response.status_code}")
    #Parse the page content using BeautifulSoup + lxml
    soup = BeautifulSoup(response.text, 'lxml')

     #Find the first <tbody> tag
    table = soup.find('tbody')

    if not table:
        print("Error finding tbody")
        return {}
    #loop through all <tr> tags in the tbody
    for row in table.find_all('tr'):
        #Find all <a> tags within the <tr> tag to get link data
        td_table = row.find_all('td')
        #get month of event
        month = td_table[1].get_text(strip=True)
        #get day of event
        days = td_table[2].get_text(strip=True)
        #get event name, remove extra strings 
        event_name = td_table[4].get_text(strip=True)
        for word in replace_list:
            event_name = event_name.replace(word, '')
        event_name = event_name + '(' + month + ' ' + days + ')'
        #get all links for each setting, append it to the dictionary
        link_dict = {}
        options = ['Raw', 'Final', 'Pax']
        for setting in options:
            link_tags = row.find_all('a', string=setting)
            links = []
            for link in link_tags:
                links.append(link['href'])
            #only return the data if there's atleast one link
            if len(links) > 0:
                link_dict[setting] = links
        #append the link dictionary to the current option if there's a link
        if len(link_dict) > 0:
            scraped_data[event_name] = link_dict
    #return scraped data, key being the name and date of event as a string for dropdown, value being the links 
    return scraped_data

def get_records(url, name, car_make, setting):
    scraped_data = []
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching page {results_url}, status code: {response.status_code}")
    #Parse the page content using BeautifulSoup + lxml
    soup = BeautifulSoup(response.text, 'lxml')

     #Find all the <tbody> tag
    t_tags = soup.find_all('tbody')
    #if pax or raw, we need the 2nd table
    table = t_tags[1]
    #if final, we need the 3rd table
    if setting == "Final":
        table = t_tags[2]
    #before doing anything, check if the name or car_make provided is in it
    found_valid_record = False
    fixed_name = name.strip().lower()
    fixed_car_make = car_make.strip().lower()
    #extra field to see which ones to use to identify fields during scraping process
    valid_identifiers = []
    if len(fixed_car_make) > 0:
        if fixed_car_make in table.get_text().lower():
            found_valid_record = True
            valid_identifiers.append(fixed_car_make)
    if len(fixed_name) > 0:
        if fixed_name in table.get_text().lower():
            found_valid_record = True
            valid_identifiers.append(fixed_name)
    #if found records, start scraping
    if found_valid_record:
        for tr in table.find_all('tr'):
            #check if the names in the current row
            in_table = False
            raw_text = tr.get_text(strip=True)
            for identifier in valid_identifiers:
               if identifier in raw_text.lower():
                   in_table = True
            #if in table, start collection data to present
            if in_table:
                output_array = []
                for td in tr.find_all('td'):
                    #if pax or raw, append to table
                    current_text = td.get_text(strip=True)
                    if setting == "Pax" or setting == "Raw":
                        output_array.append(td.get_text(strip=True))
                    #if final, check if there's any runs that weren't done, set it to N/A for convenience
                    elif setting == "Final":
                        if len(current_text) > 0:
                            output_array.append(current_text)
                        else:
                            output_array.append('N/A')
                scraped_data.append(output_array)
    return scraped_data

#helper to determine if there was 1 days or two days for the event
def determine_days(fixed_array):
    starting_index = fixed_array[0]
    next_index = fixed_array[1]
    final_index = fixed_array[2]
    #if length of string is less than 5(means its a setting), means only one day, otherwise it means two days
    if len(final_index) <= 5:
        return 1
    else:
        return 2
#fixes getting given a string from html, makes it so you dont have to rescrape
def get_links_from_string(returned_string):
    new_string = returned_string.strip()
    #start removing excess stuff from the string
    removables = ["[", "]", "{", "}", ",", " "]
    for removable in removables:
        new_string = new_string.replace(removable, '')
    new_string = new_string.split("'")
    #put it into an array
    fixed_array = []
    for item in new_string:
        if ':' in item and len(item) < 5:
            item = item.replace(':', '')
        if len(item) > 0:
            fixed_array.append(item)
    #determine number of days of event through the amount of links
    days = determine_days(fixed_array)
    #turn it into a dictionary
    final_dictionary = {}
    for i in range(0, len(fixed_array), (1+days)):
        key = fixed_array[i]
        key_array = []
        for v in range(1,days+1):
            key_array.append(fixed_array[i+v])
        final_dictionary[key] = key_array
    #return dictionary
    return final_dictionary

def get_weather(given_date):
    url = "https://api.open-meteo.com/v1/forecast"
    #latitude and longitude for rantoul
    lat = 40.294190
    lon = -88.148880
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["weathercode"],
        "start_date": given_date,
        "end_date": given_date,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "hourly" not in data:
        print("No weather data found.")
        return

    #Get weather code and timestamp data
    weather_codes = data["hourly"]["weathercode"]
    times = data["hourly"]["time"]

    #We'll get the most recent available hour starting from 10 oclock in the morning
    current_hour_index = 10
    for i in range(10, len(times)):
        if times[i]:
            current_hour_index = i
            break
    weather_code = weather_codes[current_hour_index]

    #Translate code to description
    weather_description = get_weather_from_code(weather_code)
    return weather_description

#Decode the weather code to human-readable condition(certainly didnt chatgpt this cause lazy)
def get_weather_from_code(weather_code):
    weather_conditions = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        45: 'Fog',
        48: 'Depositing rime fog',
        51: 'Light drizzle',
        53: 'Drizzle',
        55: 'Heavy drizzle',
        56: 'Light freezing drizzle',
        57: 'Freezing drizzle',
        61: 'Light rain',
        63: 'Rain',
        65: 'Heavy rain',
        66: 'Light freezing rain',
        67: 'Freezing rain',
        71: 'Light snow fall',
        73: 'Snow fall',
        75: 'Heavy snow fall',
        77: 'Snow grains',
        80: 'Light rain showers',
        81: 'Rain showers',
        82: 'Heavy rain showers',
        85: 'Light snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorms',
        96: 'Thunderstorms with light hail',
        99: 'Thunderstorms with heavy hail'
    }
    
    return weather_conditions.get(weather_code, "Unknown weather")
