from django.conf.urls import url

from . import views

app_name = 'videos'
urlpatterns = [
    url(r'^$', views.VideoListView.as_view(), name='list'),
    url(r'^new/$', views.VideoCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.VideoDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.VideoUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.VideoDeleteView.as_view(), name='delete'),
    url(r'^(?P<pk1>[0-9]+)/belongsto/(?P<pk2>[0-9]+)/$', views.VideoBelongToView.as_view(), name='belongs_to'),
]
