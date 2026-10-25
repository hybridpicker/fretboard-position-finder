# fretboard/templatetags/custom_tags.py
from django import template

register = template.Library()


@register.filter
def times(number: int) -> range:
    """Iterate from 0 up to ``number`` (exclusive)."""
    return range(number)
