from django.conf.urls import url

from . import views


app_name = 'api'
urlpatterns = [
    url(r'next/$', views.next_videos, name='next_videos'),
    url(r'watched/$', views.watched_videos, name='watched_videos'),
]
