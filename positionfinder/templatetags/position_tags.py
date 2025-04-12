from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def friendly_string_name(string_name):
    """Convert internal string name to user-friendly display name"""
    string_display = {
        'eString': 'High E (1st)',
        'bString': 'B (2nd)',
        'gString': 'G (3rd)',
        'dString': 'D (4th)',
        'AString': 'A (5th)',
        'ELowString': 'Low E (6th)',
        'highAString': 'High A (0)',
        'lowBString': 'Low B (7th)'
    }
    return string_display.get(string_name, string_name)

@register.filter
def position_description(position_order):
    """Provide a helpful description of the position"""
    descriptions = {
        1: "Open Position (0-4 Frets)",
        2: "2nd Position (2-6 Frets)",
        3: "4th Position (4-8 Frets)",
        4: "5th Position (5-9 Frets)",
        5: "7th Position (7-11 Frets)",
        6: "9th Position (9-14 Frets)",
        7: "12th Position/Octave (12-16 Frets)",
        8: "Low Extended Position (For 8-string)",
        9: "High Extended Position (For 8-string)"
    }
    return descriptions.get(position_order, f"Position {position_order}")

@register.filter
def position_difficulty(position_order):
    """Rate the difficulty of a position"""
    difficulties = {
        1: "Beginner",
        2: "Beginner-Intermediate",
        3: "Intermediate",
        4: "Intermediate",
        5: "Intermediate-Advanced",
        6: "Advanced",
        7: "Advanced",
        8: "Advanced (8-string)",
        9: "Advanced (8-string)"
    }
    return difficulties.get(position_order, "Intermediate")

@register.filter
def position_color_class(position_order):
    """Assign a color class based on position difficulty"""
    if position_order <= 2:
        return "position-beginner"
    elif position_order <= 5:
        return "position-intermediate"
    else:
        return "position-advanced"
