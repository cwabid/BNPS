from .utils import fetch_html
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_title_and_links_for_bdnews24(main_url, category_url):
    html_content = fetch_html(category_url)
    if not html_content:
        return "No Title", []

    soup = BeautifulSoup(html_content, "html.parser")
    page_title = soup.find("title").text.strip() if soup.find("title") else "No Title"

    news_links = set()
    for img_tag in soup.find_all("img"):
        parent_a = img_tag.find_parent("a", href=True)
        if parent_a:
            news_url = urljoin(main_url, parent_a["href"])
            if news_url.startswith(category_url):
                news_links.add(news_url)

    print(f"Total News Links Found: {len(news_links)}")
    print(list(news_links))

    return page_title, list(news_links)


def get_news_content_for_news24(url):
    html_content = fetch_html(url)
    if not html_content:
        return "No Title", "No Content"

    soup = BeautifulSoup(html_content, "html.parser")

    article = soup.find("div", class_="container")
    if not article:
        return "No Title", "No Content"

    title_tag = article.select_one(".details-title h1") or soup.find("title")
    title = title_tag.text.strip() if title_tag else "No Title"

    content_div = soup.find("div", id="contentDetails")
    if not content_div:
        return title, "No Content"

    paragraphs = content_div.find_all("p")
    content = "\n\n".join(p.text.strip() for p in paragraphs if p.text.strip())

    return title, content