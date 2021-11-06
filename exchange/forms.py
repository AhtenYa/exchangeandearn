from django import forms
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User

from .models import Account, Transfer
from stock.models import Currency


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['account_from', 'account_to', 'amount']
        #labels = {'amount' : '', 'transfer_date' : ''}
        widgets = {'account_from': forms.Select(attrs={'name' : 'account_from'}), 'account_to': forms.Select(attrs={'name' : 'account_to'}),
         'amount' : forms.NumberInput(attrs={'name': 'transfer_amount', 'placeholder': 'Enter Amount'})}

    def clean(self):
        cleaned_data = super().clean()
        account_from = cleaned_data.get("account_from")
        account_to = cleaned_data.get("account_to")
        amount = cleaned_data.get("amount")

        user = self.initial['user']

        balance = account_from.balance

        if account_from == account_to:
            raise ValidationError("You must choose different accounts.")
        elif amount <= 0.0:
            raise ValidationError("You must choose bigger amount.")
        elif amount > balance:
            raise ValidationError("You must choose lower amount.")
        else:
            return cleaned_data


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['currency']
        widgets = {'currency' : forms.Select(attrs={'name' : 'currency'})}

    def clean(self):
        cleaned_data = super().clean()
        account_currency = cleaned_data.get("currency")
        user = self.initial['user']

        try:
            account = Account.objects.get(owner=user, currency=account_currency)
        except:
            return cleaned_data
        else:
            raise ValidationError("You already have that account.")

"""
class CulinkOneForm(forms.ModelForm):
    class Meta:
        model = Culink
        fields = ['longlink_text']
        labels = {'longlink_text' : ''}
        widgets = {'longlink_text' : forms.URLInput(attrs={'required' : True,
            'placeholder' : 'Paste your link to shorten', 'minlength' : 15, 'class': 'form-control border border-primary border-3 rounded-3'})}


class CulinkCheckOneForm(forms.ModelForm):
    class Meta:
        model = Culink
        fields = ['shortlink_text']
        labels = {'shortlink_text' : ''}
        widgets = {'shortlink_text' : forms.TextInput(attrs={'required' : True,
            'placeholder' : 'Type your link to check', 'minlength' : 6, 'class': 'form-control border border-primary border-3 rounded-3'})}
"""

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='',
        widget=forms.TextInput(attrs={'placeholder' : 'Username', 'minlength' : 6, 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
    password = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='',
        widget=forms.TextInput(attrs={'placeholder' : 'Username', 'minlength' : 6, 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
    password1 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
    password2 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))


class PasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'Old Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
    new_password1 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'New Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
    new_password2 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder' : 'New Password', 'class': 'my-2 fs-5 form-control border border-primary border-3 rounded-3'}))
