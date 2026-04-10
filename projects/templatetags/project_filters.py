from django import template

register = template.Library()


@register.filter
def abs_value(value):
    """Return the absolute value of a number."""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value


@register.filter
def get_item(dictionary, key):
    """Access a dict value by key in templates."""
    return dictionary.get(key)
