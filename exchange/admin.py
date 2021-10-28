from django.contrib import admin

from .models import Account, Order, Transfer


class AccountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['owner']}),
        (None, {'fields': ['status']}),
        (None, {'fields': ['currency']}),
        (None, {'fields': ['balance']}),
    ]

    list_display = ('owner', 'status', 'currency', 'balance')
    list_filter = ['currency']
    search_fields = ['owner']


class OrderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['owner']}),
        ('Date information', {'fields': ['order_date']}),
        ('Date information', {'fields': ['valuation_date']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['account']}),
    ]

    list_display = ('owner', 'order_date', 'valuation_date', 'amount', 'account')
    list_filter = ['order_date']
    search_fields = ['owner']


class TransferAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['owner']}),
        ('Date information', {'fields': ['transfer_date']}),
        ('Date information', {'fields': ['valuation_date']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['account_from']}),
        (None, {'fields': ['account_to']}),
    ]

    list_display = ('owner', 'transfer_date', 'valuation_date', 'amount', 'account_from', 'account_to')
    list_filter = ['transfer_date']
    search_fields = ['owner']

admin.site.register(Account, AccountAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Transfer, TransferAdmin)
