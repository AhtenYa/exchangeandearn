from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User

from stock.models import Currency
from .models import Account, Transfer
from .forms import LoginForm, RegisterForm, PasswordForm, AccountForm, TransferForm


class IndexView(DetailView):
    template_name = 'exchange/index.html'

    def get(self, request):
        return render(request, 'exchange/index.html')


@method_decorator(login_required, name='dispatch')
class UserIndexView(DetailView):
    template_name = 'exchange/user_index.html'

    def get(self, request):
        context = {}
        account_info = {}

        account = Account.objects.get(owner=request.user)

        #account_info['status'] = account.status
        account_info['currency'] = account.currency
        account_info['balance'] = account.balance

        context['account_info'] = account_info

        return render(request, 'exchange/user_index.html', context)


@method_decorator(login_required, name='dispatch')
class UserPasswordView(PermissionRequiredMixin, PasswordChangeView):
    permission_required = 'auth.change_user'
    template_name = 'exchange/user_password.html'
    form_class = PasswordForm
    success_url = reverse_lazy('exchange:user_settings')


@method_decorator(login_required, name='dispatch')
class UserDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'auth.delete_user'
    template_name = 'exchange/user_delete.html'
    model = User
    success_url = reverse_lazy('stock:index')
    slug_field = "username"

    def has_permission(self):
        if self.request.user == self.get_object():
            perms = self.get_permission_required()
            return self.request.user.has_perms(perms)
        else:
            return False


@method_decorator(login_required, name='dispatch')
class UserSettingsView(PermissionRequiredMixin, DetailView):
    permission_required = 'auth.change_user'
    template_name = 'exchange/user_settings.html'

    def get(self, request):
        return render(request, 'exchange/user_settings.html')


class UserLoginView(LoginView):
    template_name = 'exchange/user_login.html'
    authentication_form = LoginForm
    redirect_field_name = 'exchange:user_login'
    redirect_authenticated_user = True


class UserRegisterView(CreateView):
    template_name = 'exchange/user_register.html'
    model = User
    form_class = RegisterForm
    success_url = reverse_lazy('exchange:user_login')

    def add_base_account(self, owner_obj):
        base_currency = Currency.objects.get(base_currency=True)
        Account.objects.create(owner=owner_obj, status='AC', currency=base_currency, balance=2000000, base_account=True)

    def get_success_url(self):
        user = self.object

        user_content_type = ContentType.objects.get_for_model(User)
        user_perms = Permission.objects.filter(content_type=user_content_type)
        account_content_type = ContentType.objects.get_for_model(Account)
        account_perms = Permission.objects.filter(content_type=account_content_type)
        transfer_content_type = ContentType.objects.get_for_model(Transfer)
        transfer_perms = Permission.objects.filter(content_type=transfer_content_type)

        add_user_perm = Permission.objects.get(codename='add_user')

        for perm in user_perms:
            user.user_permissions.add(perm)
        for perm in account_perms:
            user.user_permissions.add(perm)
        for perm in transfer_perms:
            user.user_permissions.add(perm)

        user.user_permissions.remove(add_user_perm)

        self.add_base_account(user)

        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)


@method_decorator(login_required, name='dispatch')
class TransferCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'exchange.add_transfer'
    template_name = 'exchange/transfer_create.html'
    model = Transfer
    form_class = TransferForm
    success_url = reverse_lazy('exchange:user_index')


@method_decorator(login_required, name='dispatch')
class AccountCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'exchange.add_account'
    template_name = 'exchange/account_create.html'
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('exchange:user_index')

    def form_valid(self, form):
        owner_obj = self.request.user
        currency_id = self.request.POST['currency']
        account_currency = Currency.objects.get(id=currency_id)

        Account.objects.create(owner=self.request.user, status='AC',
        currency=account_currency, balance=0.00, base_account=False)

        return super().form_valid(form)


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('stock:index'))
