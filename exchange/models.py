from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from stock.models import Currency


class Account(models.Model):
    class AccountStatus(models.TextChoices):
        ACTIVE = 'AC', _('Active')
        INACTIVE = 'IA', _('Inactive')
        BLOCKED = 'BL', _('Blocked')
        CLOSED = 'CL', _('Closed')


    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.FloatField(max_length=32, default=0.00000000)
    base_account = models.BooleanField(default=False)

    def __str__(self):
        return self.currency.currency_code


class Transfer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(auto_now_add=True)
    valuation_date = models.DateTimeField('valuation date')
    amount = models.FloatField(max_length=32, default=0.00000000)
    account_from = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='account_from')
    account_to = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='account_to')
