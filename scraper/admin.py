from django.contrib import admin
from .models import NewsData, NewsSources
from .tasks import start_scraping_news

@admin.register(NewsData)
class NewsDataAdmin(admin.ModelAdmin):
    list_display = ["title", "link", "date", "source"]
    search_fields = ["title", "source"]
    list_filter = ["source", "date"]
    ordering = ["-date"]

@admin.register(NewsSources)
class NewsSourcesAdmin(admin.ModelAdmin):
    list_display = ["name", "link", "total_articles" ,"status"]
    search_fields = ["name", "link"]
    actions = ["start_scraping"]

    @admin.display(description="Total Articles")
    def total_articles(self, obj):
        return NewsData.objects.filter(source=obj.name).count()

    @admin.action(description="Start Scraping Selected Sites")
    def start_scraping(self, request, queryset):
        for obj in queryset:
            url = obj.link
            name = obj.name
            start_scraping_news.delay(url, name)

