from django.contrib import admin

from .models import Account, Transfer


class AccountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['owner']}),
        (None, {'fields': ['status']}),
        (None, {'fields': ['currency']}),
        (None, {'fields': ['balance']}),
        (None, {'fields': ['base_account']}),
    ]

    list_display = ('owner', 'status', 'currency', 'balance', 'base_account')
    list_filter = ['owner', 'status', 'currency', 'base_account']
    search_fields = ['owner']


class TransferAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['owner']}),
        ('Date information', {'fields': ['valuation_date']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['account_from']}),
        (None, {'fields': ['account_to']}),
    ]

    list_display = ('owner', 'transfer_date', 'valuation_date', 'amount', 'account_from', 'account_to')
    list_filter = ['owner', 'transfer_date']
    search_fields = ['owner']

admin.site.register(Account, AccountAdmin)
admin.site.register(Transfer, TransferAdmin)
