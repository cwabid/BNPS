from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import NewsData, NewsSources

def news_view(request):
    query = request.GET.get("q", "")
    selected_source = request.GET.get("source", "")  # Get selected source from query params
    news_objects = NewsData.objects.all()
    sources = NewsSources.objects.all()  # Fetch all news sources

    # Apply search filter if query is provided
    if query:
        news_objects = news_objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    # Apply source filter if a specific source is selected
    if selected_source:
        news_objects = news_objects.filter(source=selected_source)

    total_results = news_objects.count()

    # Pagination: Show 9 news per page
    paginator = Paginator(news_objects, 9)
    page_number = request.GET.get("page")
    news_objects = paginator.get_page(page_number)

    return render(request, "list.html", {
        "news_objects": news_objects,
        "query": query,
        "total_results": total_results,
        "sources": sources,
        "selected_source": selected_source,
    })
