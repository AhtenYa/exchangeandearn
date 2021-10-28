from django.contrib import admin

from .models import Currency, CurrencyStat


class CurrencyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['currency_code']}),
        (None, {'fields': ['currency_name']}),
        (None, {'fields': ['base_currency']}),
        (None, {'fields': ['index']}),
    ]

    list_display = ('currency_code', 'currency_name', 'base_currency', 'index')
    list_filter = ['currency_code']
    search_fields = ['currency_code']


class CurrencyStatAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['currency']}),
        ('Date information', {'fields': ['effective_date']}),
        (None, {'fields': ['value_mid']}),
        (None, {'fields': ['value_bid']}),
        (None, {'fields': ['value_ask']}),
    ]

    list_display = ('currency', 'effective_date', 'value_mid', 'value_bid', 'value_ask')
    list_filter = ['currency']
    search_fields = ['currency']


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyStat, CurrencyStatAdmin)
