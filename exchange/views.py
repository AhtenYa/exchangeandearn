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
from django.utils import timezone
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User

from stock.models import Currency, CurrencyStat
from .models import Account, Transfer
from .forms import LoginForm, RegisterForm, PasswordForm, AccountForm, TransferForm

import datetime, requests, math


class IndexView(DetailView):
    template_name = 'exchange/index.html'

    def get(self, request):
        return render(request, 'exchange/index.html')


@method_decorator(login_required, name='dispatch')
class UserIndexView(DetailView):
    template_name = 'exchange/user_index.html'

    def get(self, request):
        user = request.user
        context = {}

        base_account = Account.objects.get(owner=user, base_account=True)
        other_accounts = Account.objects.filter(owner=user, base_account=False)

        context['base_account'] = base_account
        context['other_accounts'] = other_accounts

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
class TransferCreateView(PermissionRequiredMixin, FormView):
    permission_required = 'exchange.add_transfer'
    template_name = 'exchange/transfer_create.html'
    model = Transfer
    form_class = TransferForm
    success_url = reverse_lazy('exchange:user_index')

    def get_data(self, code, type):
        if code != 'PLN':
            url = f"https://api.nbp.pl/api/exchangerates/rates/c/{code}/last?format=JSON"
            try:
                data = requests.get(url).json()['rates'][0]
            except requests.exceptions.RequestException as e:
                curr = Currency.objects.get(currency_code=code)
                data = CurrencyStat.objects.filter(currency=curr).last()
                date = data.effective_date

                if type == 'ask':
                    rate = data.value_ask
                elif type == 'bid':
                    rate = data.value_bid
            else:
                rate = data[type]
                date = data['effectiveDate']
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                date = timezone.make_aware(date, timezone.get_current_timezone())
        else:
            rate = float(1)
            date = datetime.datetime.today()
            date = timezone.make_aware(date, timezone.get_current_timezone())

        return rate, date

    def get_initial(self):
        init = super(TransferCreateView, self).get_initial()
        init.update({'user':self.request.user})
        return init

    def form_valid(self, form):
        owner_obj = self.request.user
        af_id = self.request.POST['account_from']
        at_id = self.request.POST['account_to']

        amount_from = float(self.request.POST['amount_from'])
        amount_from = math.floor(amount_from * 100)/100.0

        account_from = Account.objects.get(id=af_id)
        account_to = Account.objects.get(id=at_id)

        curcode_from = account_from.currency.currency_code
        curcode_to = account_to.currency.currency_code

        rate_from, date_from = self.get_data(curcode_from, 'bid')
        rate_to, date_to = self.get_data(curcode_to, 'ask')

        amount_to = float(float(amount_from) * float(rate_from) / float(rate_to))
        amount_to = math.floor(amount_to * 100)/100.0

        account_from.balance = account_from.balance - amount_from
        account_from.balance = math.floor(account_from.balance * 100)/100.0
        account_from.save()
        account_to.balance = account_to.balance + amount_to
        account_to.balance = math.floor(account_to.balance * 100)/100.0
        account_to.save()

        Transfer.objects.create(owner=owner_obj, valuation_date_from=date_from,
        valuation_date_to=date_to, exchange_rate_from=rate_from, exchange_rate_to=rate_to,
        amount_from=amount_from, amount_to=amount_to, account_from=account_from, account_to=account_to)

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TransfersListView(PermissionRequiredMixin, ListView):
    permission_required = 'exchange.view_transfer'
    template_name = 'exchange/transfers_list_view.html'
    model = Transfer

    def get_context_data(self):
        transfers = Transfer.objects.filter(owner=self.request.user)
        transfersDesc = transfers.order_by('-transfer_date')

        paginator = Paginator(transfersDesc, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}

        return context


@method_decorator(login_required, name='dispatch')
class AccountCreateView(PermissionRequiredMixin, FormView):
    permission_required = 'exchange.add_account'
    template_name = 'exchange/account_create.html'
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('exchange:user_index')

    def get_initial(self):
        init = super(AccountCreateView, self).get_initial()
        init.update({'user':self.request.user})
        return init

    def form_valid(self, form):
        currency_id = self.request.POST['currency']
        account_currency = Currency.objects.get(id=currency_id)
        owner_obj = self.request.user

        Account.objects.create(owner=owner_obj, currency=account_currency)

        return super().form_valid(form)


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('stock:index'))
