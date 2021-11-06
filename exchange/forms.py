from django import forms
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User

from .models import Account, Transfer
from stock.models import Currency


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['amount', 'transfer_date']
        labels = {'amount' : '', 'transfer_date' : ''}
        widgets = {'amount' : forms.NumberInput(attrs={'name': 'transfer_amount', 'placeholder': 'Enter Amount'}),
                'transfer_date': forms.DateInput(attrs={'name': 'transfer_date', 'type': 'date', 'class': 'form-control datepicker'})}


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['currency']
        #labels = {'currency': ''}
        widgets = {'currency' : forms.Select(attrs={'name' : 'currency'})}

    def clean(self):
        cleaned_data = super().clean()
        account_currency = cleaned_data.get("currency")
        user = self.request.user

        try:
            account = Account.objects.get(owner=user, currency=account_currency)
        except:
            pass
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
