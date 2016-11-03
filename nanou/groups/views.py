from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
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


class GroupListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'nanou.manage_curriculum'
    model = Group
    template_name = 'groups/list.html'
    context_object_name = 'groups'


class GroupDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'nanou.manage_curriculum'
    model = Group
    template_name = 'groups/detail.html'
    context_object_name = 'group'


class GroupDeleteView(PermissionRequiredMixin, NeoDeleteView):
    permission_required = 'nanou.manage_curriculum'
    model = Group
    template_name = 'groups/delete.html'
    success_url = reverse_lazy('groups:list')
    context_object_name = 'group'


class GroupUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'nanou.manage_curriculum'
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm


class GroupCreateView(PermissionRequiredMixin, NeoCreateView):
    permission_required = 'nanou.manage_curriculum'
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm
