from django import forms

from .models import Currency

class DateFromToForm(forms.Form):
    date_from = forms.DateField(label='',
        widget=forms.DateInput(attrs={'name': 'date_from', 'type': 'date', 'class': 'form-control datepicker'}))
    date_to = forms.DateField(label='',
        widget=forms.DateInput(attrs={'name': 'date_to', 'type': 'date', 'class': 'form-control datepicker'}))


class ExchangeForm(forms.Form):
    currency_ask = forms.ModelChoiceField(queryset=Currency.objects.all().order_by('index'))
    currency_bid = forms.ModelChoiceField(queryset=Currency.objects.all().order_by('index'))
    amount = forms.DecimalField(label='', decimal_places=2,
        widget=forms.NumberInput(attrs={'name': 'amount', 'placeholder': 'Enter Amount'}))
