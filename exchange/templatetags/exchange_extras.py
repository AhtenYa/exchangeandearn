from django import template

from exchange.models import Account

register = template.Library()

@register.filter
def from_dict(dictionary, key):
    return dictionary[key]
