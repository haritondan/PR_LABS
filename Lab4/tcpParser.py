import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def parse_pages(urls):
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if 'product' is in the URL
        if 'product' in url:
            # This is the main products page, extract all product URLs
            a_tags = soup.find_all('a', href=True)
            product_urls = [urljoin(url, tag['href']) for tag in a_tags if '/product/' in tag['href']]

            # Visit each product URL and extract the product details
            for product_url in product_urls:
                product_response = requests.get(product_url)
                product_soup = BeautifulSoup(product_response.text, 'html.parser')
                p_tags = product_soup.find_all('p')

                # Only attempt to extract product details if there are at least 4 p tags
                if len(p_tags) >= 4:
                    product_details = {}
                    product_details['name'] = p_tags[0].text
                    product_details['author'] = p_tags[1].text.replace('Author: ', '')
                    product_details['price'] = p_tags[2].text.replace('Price: $', '')
                    product_details['description'] = p_tags[3].text.replace('Description: ', '')
                    print(product_details)

            # Save the text content of the main products page to a file
            with open('non_product_pages.txt', 'a', encoding='utf-8') as f:
                f.write(soup.get_text() + '\n')
        else:
            # This is not a products page, save the text content of the page to a file
            with open('non_product_pages.txt', 'a', encoding='utf-8') as f:
                f.write(soup.get_text() + '\n')

# List of all URLs on your webserver
urls = ["http://127.0.0.1:8080/", "http://127.0.0.1:8080/contacts", "http://127.0.0.1:8080/about", "http://127.0.0.1:8080/products"]
parse_pages(urls)