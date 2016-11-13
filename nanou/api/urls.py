from django.conf.urls import url

from . import views


app_name = 'api'
urlpatterns = [
    url(r'next/$', views.NextVideosView.as_view(), name='next_videos'),
    url(r'watch/$', views.WatchVideoView.as_view(), name='watch_videos'),
]
