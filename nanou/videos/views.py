from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from nanou.widgets import SemanticUISelectMultiple
from neo.views import NeoListView, NeoDetailView, NeoDeleteView, NeoUpdateView, NeoCreateView
from neo.forms import NeoForm
from groups.models import Group

from .models import Video


class VideoForm(NeoForm):
    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True
    )
    required_by_videos = forms.MultipleChoiceField(
        label='Required by videos',
        choices=[(video.id, video.name) for video in Video.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )
    required_videos = forms.MultipleChoiceField(
        label='Required videos',
        choices=[(video.id, video.name) for video in Video.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )
    required_groups = forms.MultipleChoiceField(
        label='Required by videos',
        choices=[(group.id, group.name) for group in Group.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )
    contained_in_groups = forms.MultipleChoiceField(
        label='Required videos',
        choices=[(group.id, group.name) for group in Group.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )


class VideoListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'nanou.manage_curriculum'
    model = Video
    template_name = 'videos/list.html'
    context_object_name = 'videos'


class VideoDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'nanou.manage_curriculum'
    model = Video
    template_name = 'videos/detail.html'
    context_object_name = 'video'


class VideoDeleteView(PermissionRequiredMixin, NeoDeleteView):
    permission_required = 'nanou.manage_curriculum'
    model = Video
    template_name = 'videos/delete.html'
    success_url = reverse_lazy('videos:list')
    context_object_name = 'video'


class VideoUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'nanou.manage_curriculum'
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm


class VideoCreateView(PermissionRequiredMixin, NeoCreateView):
    permission_required = 'nanou.manage_curriculum'
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm
