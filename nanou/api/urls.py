from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'next/$', views.NextVideosView.as_view(), name='next_videos'),
    url(r'watch/$', views.WatchVideoView.as_view(), name='watch_videos'),
    url(r'history/$', views.WatchHistoryView.as_view(), name='history'),
    url(r'preferences/$', views.PreferencesView.as_view(), name='preferences'),
    url(r'preferences/(?P<pk>[0-9]+)/$', views.PreferencesUpdateView.as_view(), name='preference_update'),
]
