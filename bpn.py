from bs4 import BeautifulSoup
import requests

import csv
from typing import List

CITIES = [2, 3]
BASE = 'https://www.berkeleyparentsnetwork.org'
INDEX_URL = BASE + '/daycares/search?city[]={city}'

FIELDS = {
    'city': 'field-name-daycare-city-ca',
    'type': 'field-name-field-daycare-type',
    'license': 'field-name-field-daycare-license',
    'website': 'field-name-field-website',
    'owner': 'field-name-field-daycare-owner',
    'email': 'field-name-field-email',
    'phone': 'field-name-field-daycare-phone',
    'zip': 'field-name-field-zip',
    'neighborhood': 'field-name-field-neighborhood',
    'capacity': 'field-name-field-daycare-capacity',
    'language': 'field-name-field-language',
    'ages': 'field-name-field-daycare-ages',
    'days': 'field-name-field-daycare-days',
    'hours': 'field-name-field-daycare-hours'
}

index_html = requests.get(INDEX_URL).text
index_soup = BeautifulSoup(index_html, 'lxml')

def get_index_page_preschools(soup: BeautifulSoup):
    return soup.find_all('div', {'class': 'views-row'})

def get_other_nav_links(index_soup):
    further_links = []
    nav_lis = index_soup.find_all('li', {'class': 'pager-item'})

    for li in nav_lis:
        further_links.append(li.find("a")['href'])
    return further_links

def get_city_preschools(index_soup):
    preschools = []

    preschools.extend(get_index_page_preschools(index_soup))
    nav_links = get_other_nav_links(index_soup)
    for link in nav_links:
        url = f"{BASE}{link}"
        html = requests.get(f"{BASE}{link}").text
        soup = BeautifulSoup(html, 'lxml')
        preschools.extend(get_index_page_preschools(soup))
    return preschools

def get_all_preschools(cities: List[int]):
    preschools = []
    for city in cities:
        index_url = INDEX_URL.format(city=city)
        index_html = requests.get(index_url).text
        index_soup = BeautifulSoup(index_html, 'lxml')
        city_preschools = get_city_preschools(index_soup)
        preschools.extend(city_preschools)
    return preschools

def get_preschool_info(preschool_soup):
    preschool_info = {}
    preschool_info['name'] = preschool_soup.title.text.split('|')[0].strip()
    print(preschool_info)
    for field_name, class_tag in FIELDS.items():
        soup = preschool_soup.find('div', {'class': class_tag})
        if soup:
            text = soup.text.strip()
            preschool_info[field_name] = text.split('\xa0')[-1]
    return preschool_info

def process_ages(age_field):
    return [c.split(' ')[0] for c in age_field.split(' - ')]

def write_to_csv(preschools):
    fieldnames = ['name', 'type', 'city', 'neighborhood', 'zip','days', 'hours', 'email', 'website', 'phone', 'start', 'end', 'capacity', 'language', 'license', 'owner']
    with open("preschools.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_preschool_info)

if __name__ == "__main__":
    preschools = get_all_preschools(CITIES)

    all_preschool_info = []
    for preschool in preschools:
        preschool_url = f"{BASE}{preschool.find('a')['href']}"
        preschool_html = requests.get(preschool_url).text
        preschool_soup = BeautifulSoup(preschool_html, 'lxml')
        info = get_preschool_info(preschool_soup)
        all_preschool_info.append(info)

    for preschool in all_preschool_info:
        age_field = preschool.get('ages')
        if age_field:
            start, end = process_ages(age_field)
            preschool['start'] = start
            preschool['end'] = end
            del preschool['ages']
        if 'email' in preschool:
            preschool['email'] = preschool['email'].replace(' [at] ', '@')

    write_to_csv(all_preschool_info)

