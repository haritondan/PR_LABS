from bs4 import BeautifulSoup
import requests
import json
import in_class


def extract_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    details = {}
    for li in soup.find_all('li', class_='m-value'):
        name_span = li.find('span', class_='adPage__content__features__key')
        value_span = li.find('span', class_='adPage__content__features__value')
        if name_span and value_span:
            name = name_span.text.strip()
            value = value_span.text.strip()
            details[name] = value

    details_json = json.dumps(details)

    return details_json


result_list = list(in_class.result)
print(result_list[20])
result_json = extract_product_details(result_list[20])
print(result_json)
