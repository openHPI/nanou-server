from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from neo.views import NeoListView, NeoDetailView, NeoDeleteView, NeoUpdateView, NeoCreateView
from neo.forms import NeoForm, NeoRelationshipField
from videos.models import Video

from .models import Group


class GroupForm(NeoForm):
    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True
    )
    required_by_videos = NeoRelationshipField(
        label='Required by videos',
        model=Video,
    )
    contained_videos = NeoRelationshipField(
        label='Contained videos',
        model=Video,
    )


class GroupListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'base.manage_curriculum'
    model = Group
    template_name = 'groups/list.html'
    context_object_name = 'groups'


class GroupDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'base.manage_curriculum'
    model = Group
    template_name = 'groups/detail.html'
    context_object_name = 'group'


class GroupDeleteView(PermissionRequiredMixin, NeoDeleteView):
    permission_required = 'base.manage_curriculum'
    model = Group
    template_name = 'groups/delete.html'
    success_url = reverse_lazy('groups:list')
    context_object_name = 'group'


class GroupUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'base.manage_curriculum'
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm


class GroupCreateView(PermissionRequiredMixin, NeoCreateView):
    permission_required = 'base.manage_curriculum'
    model = Group
    template_name = 'groups/form.html'
    success_url = reverse_lazy('groups:list')
    form_class = GroupForm
