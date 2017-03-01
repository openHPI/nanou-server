from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'videos/$', views.NextVideosView.as_view(), name='next_videos'),
    url(r'watches/$', views.WatchVideoView.as_view(), name='watch_videos'),
    url(r'history/$', views.WatchHistoryView.as_view(), name='history'),
    url(r'preferences/$', views.PreferencesView.as_view(), name='preferences'),
    url(r'preferences/(?P<pk>[0-9]+)/$', views.PreferencesUpdateView.as_view(), name='preference_update'),
    url(r'surveys/latest/$', views.SurveyView.as_view(), name='survey_latest'),
    url(r'surveys/(?P<pk>[0-9]+)/complete/$', views.SurveyCompleteView.as_view(), name='survey_complete'),
]
