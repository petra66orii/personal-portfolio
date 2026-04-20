from django.contrib.sitemaps import Sitemap
from .models import BlogPost, Service

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "/",
            "/about",
            "/services",
            "/blog",
            "/contact",
            "/custom-web-development-agency",
            "/custom-web-developer-ireland",
            "/web-development-agency-galway",
            "/web-development-agency-dublin",
            "/django-react-developer",
            "/international-web-development",
        ]

    def location(self, item):
        return item
    

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


class ServiceSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Service.objects.filter(active=True)

    def location(self, obj):
        return f"/services/{obj.slug}"
