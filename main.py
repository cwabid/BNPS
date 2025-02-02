import httpx
from bs4 import BeautifulSoup
import re
from file_handler import save_news_to_csv


def create_session():
    return httpx.Client(
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
            "TE": "trailers"
        }
    )


def make_request(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.content
    except httpx.RequestError as e:
        print(f"❌ Request failed: {e}")
        return None


def extract_unique_navigation_urls(html_content, base_url="https://www.thedailystar.net"):
    try:
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        unique_links = {}

        for ul in soup.find_all("ul", class_="sub-category-menu"):
            for li in ul.find_all("li"):
                a_tag = li.find("a")
                if a_tag:
                    title = a_tag.text.strip()
                    link = a_tag.get("href", "")
                    if link.startswith("/"):
                        link = base_url + link
                    unique_links[link] = title

        return [{"title": title, "url": link} for link, title in unique_links.items()]
    except Exception as e:
        print(f"❌ Error extracting categories: {e}")
        return []


def extract_news_links(html_content, page, base_url="https://www.thedailystar.net"):
    try:
        if not html_content or not page:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        pattern = re.compile(f"^/news/{page}/.*$")
        news_links = {}

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            match = pattern.match(href)
            if match:
                full_url = base_url + href
                news_links[full_url] = a_tag.text.strip()

        return [{"title": title, "url": url} for url, title in news_links.items()]
    except Exception as e:
        print(f"❌ Error extracting news links: {e}")
        return []


def extract_unique_news(html_content):
    try:
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles = soup.find_all("article", class_="article-section")
        news_data = {}

        for article in articles:
            title_tag = article.find("h1", class_="article-title")
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            content_section = article.find("div", class_="pb-20 clearfix")
            paragraphs = [p.get_text(strip=True) for p in content_section.find_all("p")] if content_section else []
            content = " ".join(paragraphs) if paragraphs else "No Content"

            news_data[title] = content

        return [{"title": title, "content": content} for title, content in news_data.items()]
    except Exception as e:
        print(f"❌ Error extracting news: {e}")
        return []


def fetch_categories(session, url):
    print("🔎 Fetching categories...")
    html_content = make_request(session, url)
    if not html_content:
        print("❌ Failed to fetch main page. Exiting.")
        return []

    categories = extract_unique_navigation_urls(html_content)
    if not categories:
        print("❌ No categories found. Exiting.")
        return []

    print(f"✅ Found {len(categories)} categories.")
    return categories


def scrape_category_news(session, category):
    print(f"\n🌍 Scraping category: {category['title']} ({category['url']})")

    category_page = make_request(session, category["url"])
    if not category_page:
        print(f"❌ Skipping {category['title']} due to failed request.")
        return []

    news_links = extract_news_links(category_page, category["title"].lower())
    if not news_links:
        print(f"❌ No news found in {category['title']}.")
        return []

    print(f"✅ Found {len(news_links)} news articles in {category['title']}.")
    return news_links


def scrape_news_article(session, news):
    print(f"\n📰 Fetching news: {news['title']}")

    news_page = make_request(session, news["url"])
    if not news_page:
        print(f"❌ Failed to fetch content for: {news['title']}")
        return []

    extracted_news = extract_unique_news(news_page)
    if not extracted_news:
        print(f"❌ No content extracted for: {news['title']}")
        return []

    print(f"📝 Extracted {len(extracted_news)} articles from this page.")
    return extracted_news


def save_data(news_data, filename):
    if news_data:
        flat_news_data = [news for sublist in news_data for news in sublist]
        save_news_to_csv(flat_news_data, filename)
    else:
        print("❌ No news data to save.")


def main():
    session = create_session()
    url = "https://www.thedailystar.net/news"

    categories = fetch_categories(session, url)
    if not categories:
        return

    all_news_data = []

    for category in categories:
        news_links = scrape_category_news(session, category)
        if not news_links:
            continue

        for news in news_links:
            news_data = scrape_news_article(session, news)
            if news_data:
                all_news_data.append(news_data)

    save_data(news_data=all_news_data, filename='data/thedailystar.csv')
    session.close()


if __name__ == "__main__":
    main()
