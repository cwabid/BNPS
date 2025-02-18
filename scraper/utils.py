import requests
import random
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def fetch_html(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.warning(f"Error fetching {url}: {e}")
        return None


def get_category_pages_links(main_url):
    html_content = fetch_html(main_url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    category_links = set()

    for link in soup.find_all("a", href=True):
        href = urljoin(main_url, link["href"]) if link["href"].startswith("/") else link["href"]
        if href.startswith(main_url) and len(href.split("/")) == 4 and href != main_url:
            category_links.add(href)
    logging.info(f'Total Category Links Found {len(list(category_links))}')
    logging.info(list(category_links))
    return list(category_links)


def get_title_and_links(main_url, category_url):
    html_content = fetch_html(category_url)
    if not html_content:
        return "No Title", []

    soup = BeautifulSoup(html_content, "html.parser")
    page_title = soup.find("title").text.strip() if soup.find("title") else "No Title"

    news_links = set()
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a", href=True)
        if a_tag:
            news_url = urljoin(main_url, a_tag["href"])
            if news_url.startswith(category_url):
                news_links.add(news_url)
    logging.info(f"Total News Link Found {len(list(news_links))}")
    logging.info(list(news_links))
    return page_title, list(news_links)


def get_news_content(url):
    html_content = fetch_html(url)
    if not html_content:
        return None, None

    soup = BeautifulSoup(html_content, "html.parser")
    article = soup.find("article") or soup.find("div", class_="news-content")

    if not article:
        return None, None

    title_tag = article.find("h1") or soup.find("title")
    title = title_tag.text.strip() if title_tag else "No Title"

    content_paragraphs = [p.text.strip() for p in article.find_all("p") if p.text.strip()]
    content = "\n".join(content_paragraphs) if content_paragraphs else "No Content"

    return title, content


def scrape_news(main_url):
    categories = get_category_pages_links(main_url)
    
    for category_url in categories:
        page_title, news_links = get_title_and_links(main_url, category_url)
        logging.info(f"Scraping Category: {page_title} ({category_url})")

        for news in news_links:
            title, content = get_news_content(news)
            #logging.info(f"Title: {title}\nContent: {content[:200]}...")


