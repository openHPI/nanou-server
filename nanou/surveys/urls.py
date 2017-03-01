from django.conf.urls import url

from . import views

app_name = 'surveys'
urlpatterns = [
    url(r'^$', views.SurveyListView.as_view(), name='list'),
    url(r'^new/$', views.SurveyCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.SurveyDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.SurveyUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.SurveyDeleteView.as_view(), name='delete'),
]
