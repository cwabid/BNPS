from django.db import transaction, IntegrityError
from .models import NewsData, NewsSources
import logging

logger = logging.getLogger(__name__)

def store_news_to_db(title, link, content, source_name, source_link):
    if not title or not link or not content:
        return "Invalid Data"

    try:
        with transaction.atomic():
            source, _ = NewsSources.objects.get_or_create(name=source_name, link=source_link)

            news, created = NewsData.objects.get_or_create(
                link=link,
                defaults={
                    "title": title,
                    "content": content,
                    "source": source.name
                }
            )
            
            if created:
                logger.info(f"News stored: {title}")
                return f"News stored: {title}"
            else:
                return f"News already exists: {title}"

    except IntegrityError as e:
        logger.error(f"Database IntegrityError: {e}")
        return "Database Error: Integrity Constraint Violated"
    except Exception as e:
        logger.error(f"Error storing news: {e}")
        return f"Error storing news: {str(e)}"
