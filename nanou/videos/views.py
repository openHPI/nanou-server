from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
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


class VideoListView(LoginRequiredMixin, NeoListView):
    model = Video
    template_name = 'videos/list.html'
    context_object_name = 'videos'


class VideoDetailView(LoginRequiredMixin, NeoDetailView):
    model = Video
    template_name = 'videos/detail.html'
    context_object_name = 'video'


class VideoDeleteView(LoginRequiredMixin, NeoDeleteView):
    model = Video
    template_name = 'videos/delete.html'
    success_url = reverse_lazy('videos:list')
    context_object_name = 'video'


class VideoUpdateView(LoginRequiredMixin, NeoUpdateView):
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm


class VideoCreateView(LoginRequiredMixin, NeoCreateView):
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm
