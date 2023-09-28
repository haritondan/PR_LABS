from bs4 import BeautifulSoup
import requests
import re



def scrape_page(url, max_page_num=None, page_num=1, url_list=[]):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    base_url = 'https://999.md'

    # Extract URLs and filter out boosters
    # You'll need to replace 'your-link-tag' and 'your-link-attribute' with the actual tag and attribute that hold the URLs
    for link in soup.find_all('a'):
        url = link.get('href')
        if url and re.match(r'/ro/\d+', url) and 'booster' not in url:
            absolute_url = base_url + url
            url_list.append(absolute_url)

    # Check for more pages
    # You'll need to replace 'your-pagination-tag' and 'your-pagination-attribute' with the actual tag and attribute that hold the pagination links
    next_page = soup.find('a', attrs={'href': url + '?page=' + str(page_num)})  # or however the site indicates the next page
    if next_page and (not max_page_num or page_num < max_page_num):
        next_page_url = next_page.get('href')
        return scrape_page(next_page_url, max_page_num, page_num + 1, url_list)
    else:
        return url_list

result = scrape_page("https://999.md/ro/list/audio-video-photo/microphones")

with open('urls.txt', 'a') as f:
    for url in result:
        f.write(url + '\n')