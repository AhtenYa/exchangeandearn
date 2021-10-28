import datetime

from django import template

from stock.models import Currency, CurrencyStat

register = template.Library()

@register.filter
def from_dictionary(dictionary, key):
    return dictionary[key]

@register.filter
def from_dictionary_get_currency_index_minus_one(dictionary, key):
    currency = Currency.objects.get(currency_code=key)
    currency_index = currency.index - 1
    return currency_index

@register.filter
def date_from_datetime(dt):
    date = dt.strftime('%Y-%m-%d')
    return date
