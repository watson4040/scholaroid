from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Return the value from a dictionary by key, or None if not found."""
    if dictionary is None:
        return None
    return dictionary.get(key)