from bs4 import BeautifulSoup
import requests
import re

def scrape_page(url, max_page_num=None, page_num=1, url_set=set()):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    base_url = 'https://999.md'

    for link in soup.find_all('a'):
        url = link.get('href')
        if url and re.match(r'/ro/\d+', url) and 'booster' not in url:
            absolute_url = base_url + url
            url_set.add(absolute_url)

    next_page = soup.find('a', href=lambda href: href and "?page=" + str(page_num) in href)
    if next_page and (not max_page_num or page_num < max_page_num):
        next_page_url = next_page.get('href')
        return scrape_page(next_page_url, max_page_num, page_num + 1, url_set)
    else:
        return url_set

result = scrape_page("https://999.md/ro/list/audio-video-photo/microphones")

with open('urls.txt', 'w') as f:
    for url in result:
        f.write(url + '\n')