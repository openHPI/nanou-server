"""nanou URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # manage views
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^', include('base.urls', namespace='landingpage')),
    url(r'^groups/', include('groups.urls', namespace='groups')),
    url(r'^neo/', include('neoextras.urls', namespace='neoextras')),
    url(r'^socialusers/', include('socialusers.urls', namespace='socialusers')),
    url(r'^videos/', include('videos.urls', namespace='videos')),

    # user views
    url(r'^social/', include('socialusers.urls_login', namespace='sociallogin')),
    url(r'^api/', include('api.urls', namespace='api')),
]
