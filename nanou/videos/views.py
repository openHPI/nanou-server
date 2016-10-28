from django import forms
from django.urls import reverse_lazy

from nanou.widgets import SemanticUISelectMultiple
from neo.views import NeoListView, NeoDetailView, NeoDeleteView, NeoUpdateView, NeoCreateView

from models import Video


class VideoForm(forms.Form):
    name = forms.CharField(
        label='Your name',
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


class VideoListView(NeoListView):
    model = Video
    template_name = 'videos/list.html'
    context_object_name = 'videos'


class VideoDetailView(NeoDetailView):
    model = Video
    template_name = 'videos/detail.html'
    context_object_name = 'video'


class VideoDeleteView(NeoDeleteView):
    model = Video
    template_name = 'videos/delete.html'
    success_url = reverse_lazy('videos:list')
    context_object_name = 'video'


class VideoUpdateView(NeoUpdateView):
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm


class VideoCreateView(NeoCreateView):
    model = Video
    template_name = 'videos/form.html'
    success_url = reverse_lazy('videos:list')
    form_class = VideoForm
