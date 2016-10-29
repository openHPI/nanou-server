from django import forms
from django.urls import reverse_lazy

from nanou.widgets import SemanticUISelectMultiple
from neo.views import NeoListView, NeoDetailView, NeoDeleteView, NeoUpdateView, NeoCreateView
from neo.forms import NeoForm
from videos.models import Video

from .models import Group


class GroupForm(NeoForm):
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
    contained_videos = forms.MultipleChoiceField(
        label='Contained videos',
        choices=[(video.id, video.name) for video in Video.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )


class GroupListView(NeoListView):
    model = Group
    template_name = 'groups/list.html'
    context_object_name = 'groups'


class GroupDetailView(NeoDetailView):
    model = Group
    template_name = 'groups/detail.html'
    context_object_name = 'group'


class GroupDeleteView(NeoDeleteView):
    model = Group
    template_name = 'groups/delete.html'
    success_url = reverse_lazy('groups:list')
    context_object_name = 'group'


class GroupUpdateView(NeoUpdateView):
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm


class GroupCreateView(NeoCreateView):
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm
