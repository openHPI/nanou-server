from django.conf.urls import url

from . import views_login as views

app_name = 'sociallogin'
urlpatterns = [
    url(r'^auth-status/$', views.AuthStatusView.as_view(), name='status'),
    url(r'^login-providers/$', views.LoginProvidersView.as_view(), name='login_providers'),
    url(r'^test-login/$', views.TestLoginView.as_view(), name='test_login'),
    url(r'^combine/$', views.CombineAccountsView.as_view(), name='combine_accounts'),
]
