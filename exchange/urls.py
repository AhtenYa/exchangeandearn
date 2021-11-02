from django.urls import path

from . import views

app_name = 'exchange'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('index/', views.UserIndexView.as_view(), name='user_index'),
    path('index/settings', views.UserSettingsView.as_view(), name='user_settings'),
    path('index/logout', views.logout_view, name='logout'),
]
