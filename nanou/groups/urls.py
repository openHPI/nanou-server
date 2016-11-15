from django.conf.urls import url

from . import views

app_name = 'groups'
urlpatterns = [
    url(r'^$', views.GroupListView.as_view(), name='list'),
    url(r'^new/$', views.GroupCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.GroupDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.GroupUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.GroupDeleteView.as_view(), name='delete'),
]
