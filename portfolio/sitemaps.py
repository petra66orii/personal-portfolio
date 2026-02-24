from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Project

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "services",
            "service_discovery",
            "service_foundation",
            "service_commerce",
            "service_application",
            "blog_index",
            "contact",
        ]

    def location(self, item):
        return reverse(item)
    

class BlogPostSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        # Only published posts should be indexable
        return BlogPost.objects.filter(published=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/blog/{obj.slug}"


class ProjectSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return f"/projects/{obj.id}"