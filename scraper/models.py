from django.db import models

class NewsData(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    source = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'News Data'
        verbose_name_plural = 'News Data'


class NewsSources(models.Model):
    name = models.CharField(max_length=200)
    link = models.URLField(unique=True)
    status = models.BooleanField(db_default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'News Source'
        verbose_name_plural = 'News Sources'
