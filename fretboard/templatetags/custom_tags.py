# fretboard/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def times(number):
    return range(number)
