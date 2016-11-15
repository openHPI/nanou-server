from django.conf.urls import url

from . import views

app_name = 'sociallogin'
urlpatterns = [
    url(r'^status/$', views.AuthStatusView.as_view(), name='status'),
    url(r'^login-providers/$', views.LoginProvidersView.as_view(), name='login_providers'),
]
