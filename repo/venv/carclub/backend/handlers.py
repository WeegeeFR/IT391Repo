import requests
from bs4 import BeautifulSoup

#base url to results page
results_url = "https://ccsportscarclub.org/autocross/schedule/pastresults/2023-autocross-results/"
replace_list = ['FinalRawPax', 'RawPaxFinal', 'Grudges', 'Saturday', 'Sunday', 'finalrawpax']

#valid settings are 'Raw' 'Pax' and 'Final'
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
        #append the link dictionary to the current option
        scraped_data[event_name] = link_dict
    #return scraped data, key being the name and date of event as a string for dropdown, value being the links 
    return scraped_data