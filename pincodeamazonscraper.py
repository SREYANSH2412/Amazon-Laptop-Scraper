from selectorlib import Extractor
import requests
import json
import jsonlines
import gzip
from time import sleep

# Create an Extractor by reading from the YAML file
e_amazon = Extractor.from_yaml_file('selectors.yml')
e_search_results = Extractor.from_yaml_file('search_results.yml')

# This function 'scrape_search_results' scrapes search result pages from a specified Amazon URL using custom HTTP headers.
# It performs error checks for page access and utilizes 'e_search_results.extract' to process and return the scraped data.
def scrape_amazon(url):
    # The 'headers' dictionary mimics a browser request to enhance the likelihood of successfully scraping web content.
    # It includes fields like 'User-Agent' for browser identification and 'Accept' for preferred content types.
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.in/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)

    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s has been blocked by Amazon. Consider retrying with a different proxy or VPN\n" % url)
        else:
            print("Amazon appears to have blocked page %s, as indicated by the status code %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e_amazon.extract(r.text)

# This function 'scrape_search_results' scrapes search result pages from a specified Amazon URL using custom HTTP headers.
# It performs error checks for page access and utilizes 'e_search_results.extract' to process and return the scraped data.
def scrape_search_results(url):
    # The 'headers' dictionary mimics a browser request to enhance the likelihood of successfully scraping web content.
    # It includes fields like 'User-Agent' for browser identification and 'Accept' for preferred content types.
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.in/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)

    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s has been blocked by Amazon. Consider retrying with a different proxy or VPN\n" % url)
        else:
            print("Amazon appears to have blocked page %s, as indicated by the status code %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e_search_results.extract(r.text)


num_pages=20      #number of pages
pincodes=["560001", "110001"]      #pincode location for Bangalore and Delhi
# Example usage for Search Results scraping
with open('modified_urls.txt', 'w') as text_file:
    for pincode in pincodes:
        for page_num in range(1, num_pages + 1):
            data = scrape_search_results('http://amazon.in/s?k=laptops&page={page_num}&pincode={pincode}')  #url for amazon website which search laptops, page number and pincode
            if data:
                for product in data['products']:
                    if 'url' in product:
                        laptop_url = 'https://www.amazon.in' + product['url']
                        text_file.write(laptop_url + '\n')

# Example usage for Amazon scraping
data_list = []  # List to accumulate data from each URL

with open("modified_urls.txt", 'r') as urllist:
    for url in urllist.read().splitlines():
        data = scrape_amazon(url)
        if data:
            data_list.append(data)

# Write the data to a Gzip-compressed NDJSON file
with gzip.open('output_amazon.ndjson.gz', 'wt', encoding='utf-8') as outfile:
    writer = jsonlines.Writer(outfile)
    writer.write_all(data_list)
    writer.close()


