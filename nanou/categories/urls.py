from django.conf.urls import url

from . import views

app_name = 'categories'
urlpatterns = [
    url(r'^$', views.CategoryListView.as_view(), name='list'),
    url(r'^new/$', views.CategoryCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.CategoryDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.CategoryUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.CategoryDeleteView.as_view(), name='delete'),
]
