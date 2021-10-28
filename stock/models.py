from django.db import models


class Currency(models.Model):
    def index_increment():
        last = Currency.objects.all().last()
        if not last:
            return 0
        return last.index + 1

    currency_code = models.TextField(max_length=3, unique=True)
    currency_name = models.TextField(max_length=255, unique=True)
    base_currency = models.BooleanField(default=False)
    index = models.IntegerField(default=index_increment, unique=True)

    def __str__(self):
        return self.currency_code


class CurrencyStat(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    effective_date = models.DateTimeField('effective date')
    value_mid = models.FloatField(max_length=16, default=0.00000000)
    value_bid = models.FloatField(max_length=16, default=0.00000000)
    value_ask = models.FloatField(max_length=16, default=0.00000000)
