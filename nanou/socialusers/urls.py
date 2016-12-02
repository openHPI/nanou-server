from django.conf.urls import url

from . import views

app_name = 'socialusers'
urlpatterns = [
    url(r'^$', views.SocialUserListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.SocialUserDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.SocialUserUpdateView.as_view(), name='update'),
    url(r'^(?P<pk1>[0-9]+)/preference/(?P<pk2>[0-9]+)/$',
        views.SocialUserHasPreferenceView.as_view(), name='has_preference'),
    url(r'^(?P<pk1>[0-9]+)/watched/(?P<pk2>[0-9]+)/$', views.SocialUserWatchedView.as_view(), name='watched'),
]
