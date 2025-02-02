from scrape_helper import extract_links_from_pages, extract_titles_and_links

import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None

def main(url):
    try:
        html_content = fetch_html(url)
        if not html_content:
            return {'headline_links': [], 'section_titles_and_links': []}

        headline_links = extract_links_from_pages(html_content)
        section_titles_and_links = extract_titles_and_links(html_content)

        return {'headline_links': headline_links, 'section_titles_and_links': section_titles_and_links}
    except Exception:
        return {'headline_links': [], 'section_titles_and_links': []}


print(main("https://en.prothomalo.com/bangladesh"))