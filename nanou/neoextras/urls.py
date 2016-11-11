from django.conf.urls import url

from . import views


app_name = 'neoextras'
urlpatterns = [
    url(r'^relations/(?P<pk1>[0-9]+)/(?P<rel_type>[\w\-\_]+)/(?P<pk2>[0-9]+)/$',
        views.NeoRelationshipDetailView.as_view(), name='relation'),
]
