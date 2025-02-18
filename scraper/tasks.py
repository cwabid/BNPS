import logging
from celery import shared_task
from .utils import get_category_pages_links, get_title_and_links, get_news_content
from .all_news_paper import get_title_and_links_for_bdnews24, get_news_content_for_news24
from .save_data import store_news_to_db
from .models import NewsSources
import time
logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def start_scraping_news(self, main_url, source):
    logger.info(f"Starting scraping for {source} - {main_url}")

    category_links = get_category_pages_links(main_url)
    if not category_links:
        logger.warning(f"No category links found for {main_url}")
        return "No categories found."

    news_links = set()
    for category_link in category_links:
        if main_url.__contains__("bdnews24"):
            _, links = get_title_and_links_for_bdnews24(main_url, category_link)
        else:
            _, links = get_title_and_links(main_url, category_link)
        news_links.update(links)

    if not news_links:
        logger.warning(f"No news articles found for {main_url}")
        return "No news articles found."

    for news_url in news_links:

        start_fetching_news_content.delay(news_url, source, main_url)

    logger.info(f"Scraping initiated, {len(news_links)} articles found for {source}.")
    return f"Scraping initiated, {len(news_links)} articles found."

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def start_fetching_news_content(self, content_url, source, main_url):
    logger.info(f"Fetching content for: {content_url}")
    if content_url.__contains__("bdnews24"):
        title, content = get_news_content_for_news24(content_url)
    else:    
        title, content = get_news_content(content_url)
    if not title or not content:
        logger.warning(f"Failed to fetch content for {content_url}")
        return f"Failed to fetch content for {content_url}"

    store_news_to_db(title, content_url, content, source, main_url)
    
    logger.info(f"Stored article: {title}")
    return f"Stored article: {title}"


@shared_task(bind=True)
def automate_task(self):
    try:
        sources = NewsSources.objects.filter(status=True).values_list("link", "name")
        sources = list(sources)

        if not sources:
            logger.info("No sources found for scraping.")
            return "No sources available."

        total_sources = len(sources)
        logger.info(f"Starting scraping for {total_sources} sources.")

        for index, (link, name) in enumerate(sources, start=1):
            try:
                start_scraping_news.apply_async(args=[link, name], countdown=index * 5)
                logger.info(f"Task {index}/{total_sources} queued for: {name} ({link})")
            except Exception as e:
                logger.error(f"Error queuing scraping task for {name}: {str(e)}")

            time.sleep(2)

        logger.info("All sources have been queued successfully.")
        return f"Scraping tasks queued for {total_sources} sources."

    except Exception as e:
        logger.error(f"Automate Task Failed: {str(e)}")
        return f"Error occurred: {str(e)}"
