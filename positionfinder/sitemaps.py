"""
Sitemap generation for better SEO.
This creates a sitemap.xml file for search engines.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages like home, about, etc."""

    priority = 0.8
    changefreq = "weekly"
    # The site is served over HTTPS (https://fretboard.schoensgibl.com); the host
    # itself comes from the request because django.contrib.sites is not installed.
    protocol = "https"

    def items(self) -> list[str]:
        """Return the URL names included in the sitemap."""
        return ["fretboard", "about", "impressum"]

    def location(self, item: str) -> str:
        """Return the URL path for a URL name."""
        return reverse(item)
