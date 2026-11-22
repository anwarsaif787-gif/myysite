from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import BlogPost, Service


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "clinic:home",
            "clinic:about",
            "clinic:services",
            "clinic:testimonials",
            "clinic:gallery",
            "clinic:blog",
            "clinic:faq",
            "clinic:contact",
            "clinic:book",
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Service.objects.all()


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at
