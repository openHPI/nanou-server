from django.conf.urls import url

from . import views_login as views

app_name = 'sociallogin'
urlpatterns = [
    url(r'^auth-status/$', views.AuthStatusView.as_view(), name='status'),
    url(r'^login-providers/$', views.LoginProvidersView.as_view(), name='login_providers'),
]
