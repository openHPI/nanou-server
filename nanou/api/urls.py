from django.conf.urls import url

from . import views


app_name = 'api'
urlpatterns = [
    url(r'next/$', views.next_videos, name='next_videos'),
    url(r'watched/(?P<video_id>[0-9]+)/$', views.watched_video, name='watched_video'),
]
