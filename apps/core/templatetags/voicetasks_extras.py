"""
Custom template filters and tags for VoiceTasks.
"""
import json

from django import template

register = template.Library()


@register.filter(name='tojson')
def to_json(value):
    """
    Serialize a Python value to a JSON string.

    Usage in templates: {{ my_string|tojson }}
    Produces a properly escaped JSON-encoded string literal (with quotes).
    """
    return json.dumps(value)


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Dictionary lookup by variable key.

    Usage: {{ my_dict|get_item:key_variable }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
