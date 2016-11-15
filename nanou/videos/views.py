from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from groups.models import Group
from neo.forms import (NeoForm, NeoRelationshipField,
                       NeoRelationshipNoSelfRefField)
from neo.views import (NeoCreateView, NeoDeleteView, NeoDetailView,
                       NeoListView, NeoUpdateView)

from .models import Video


class VideoForm(NeoForm):
    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True
    )
    required_by_videos = NeoRelationshipNoSelfRefField(
        label='Required by videos',
        model=Video,
    )
    required_videos = NeoRelationshipNoSelfRefField(
        label='Required videos',
        model=Video,
    )
    required_groups = NeoRelationshipField(
        label='Required by videos',
        model=Group,
    )
    contained_in_groups = NeoRelationshipField(
        label='Required videos',
        model=Group,
    )


class VideoListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'base.manage_curriculum'
    model = Video
    template_name = 'videos/list.html'
    context_object_name = 'videos'


class VideoDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'base.manage_curriculum'
    model = Video
    template_name = 'videos/detail.html'
    context_object_name = 'video'


class VideoDeleteView(PermissionRequiredMixin, NeoDeleteView):
    permission_required = 'base.manage_curriculum'
    model = Video
    template_name = 'videos/delete.html'
    success_url = reverse_lazy('videos:list')
    context_object_name = 'video'


class VideoUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'base.manage_curriculum'
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm


class VideoCreateView(PermissionRequiredMixin, NeoCreateView):
    permission_required = 'base.manage_curriculum'
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm
