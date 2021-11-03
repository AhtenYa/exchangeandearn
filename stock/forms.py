from django import forms
from django.core.exceptions import ValidationError

from .models import Currency

class DateFromToForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'name': 'date_from', 'type': 'date', 'class': 'form-control datepicker'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'name': 'date_to', 'type': 'date', 'class': 'form-control datepicker'}))

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from > date_to:
            raise ValidationError("Invalid date range.")


class ExchangeForm(forms.Form):
    currency_ask = forms.ModelChoiceField(queryset=Currency.objects.all().order_by('index'), empty_label=None)
    currency_bid = forms.ModelChoiceField(queryset=Currency.objects.all().order_by('index'), empty_label=None)
    ask_amount = forms.DecimalField(label='', decimal_places=2,
        widget=forms.NumberInput(attrs={'name': 'ask_amount', 'placeholder': 'Enter Amount'}))
