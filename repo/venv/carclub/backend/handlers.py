import requests
from bs4 import BeautifulSoup

#base url to results page
results_url = "https://ccsportscarclub.org/autocross/schedule/pastresults/2023-autocross-results/"

def scrape_season_events(setting):
    response = requests.get(results_url)
    if response.status_code != 200:
        raise Exception(f"Error fetching page {results_url}, status code: {response.status_code}")
    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup)

scrape_season_events("raw")