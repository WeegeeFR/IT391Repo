import requests
from bs4 import BeautifulSoup

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

def get_raw_pax_records(url, name, car_make, setting):
    scraped_data = []
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching page {results_url}, status code: {response.status_code}")
    #Parse the page content using BeautifulSoup + lxml
    soup = BeautifulSoup(response.text, 'lxml')

     #Find all the <tbody> tag
    t_tags = soup.find_all('tbody')
    #get the one we need(2nd)
    table = t_tags[1]
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
                    output_array.append(td.get_text(strip=True))
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