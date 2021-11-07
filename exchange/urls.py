from django.urls import path

from . import views

app_name = 'exchange'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/logout', views.logout_view, name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('profile/', views.UserIndexView.as_view(), name='user_index'),
    path('profile/accounts/', views.AccountCreateView.as_view(), name='account_create'),
    path('profile/transfers/', views.TransfersListView.as_view(), name='transfers_list_view'),
    path('profile/transfers/create', views.TransferCreateView.as_view(), name='transfer_create'),
    path('profile/settings', views.UserSettingsView.as_view(), name='user_settings'),
    path('profile/password', views.UserPasswordView.as_view(), name='user_password'),
    path('profile/delete/<slug:slug>', views.UserDeleteView.as_view(), name='user_delete'),
]
