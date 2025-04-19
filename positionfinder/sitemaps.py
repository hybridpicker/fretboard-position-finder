"""
Sitemap generation for better SEO.
This creates a sitemap.xml file for search engines.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages like home, about, etc."""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['fretboard', 'about', 'impressum']
    
    def location(self, item):
        return reverse(item)
