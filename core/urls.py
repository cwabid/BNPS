
from django.contrib import admin
from django.urls import path
from scraper.views import news_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", news_view, name="news_view"),

]
