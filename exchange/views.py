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

from .models import Account, Order, Transfer
from .forms import LoginForm, RegisterForm, PasswordForm


class IndexView(DetailView):
    template_name = 'exchange/index.html'

    def get(self, request):
        return render(request, 'exchange/index.html')


class UserIndexView(DetailView):
    template_name = 'exchange/user_index.html'

    def get(self, request):
        return render(request, 'exchange/user_index.html')


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
        order_content_type = ContentType.objects.get_for_model(Order)
        order_perms = Permission.objects.filter(content_type=order_content_type)
        transfer_content_type = ContentType.objects.get_for_model(Transfer)
        transfer_perms = Permission.objects.filter(content_type=transfer_content_type)

        add_user_perm = Permission.objects.get(codename='add_user')

        for perm in user_perms:
            user.user_permissions.add(perm)
        for perm in account_perms:
            user.user_permissions.add(perm)
        for perm in order_perms:
            user.user_permissions.add(perm)
        for perm in transfer_perms:
            user.user_permissions.add(perm)

        user.user_permissions.remove(add_user_perm)

        self.add_base_account(user)

        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('stock:index'))
