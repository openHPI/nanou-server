from django.conf.urls import url

from . import views


app_name = 'sociallogin'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logged-in/$', views.login_success, name='logged_in'),
]
