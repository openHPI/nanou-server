from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from neo.forms import NeoForm, NeoRelationshipField
from neo.views import NeoCreateView, NeoDeleteView, NeoDetailView, NeoListView, NeoUpdateView
from videos.models import Video

from .models import Category


class CategoryForm(NeoForm):
    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True
    )
    videos = NeoRelationshipField(
        label='Videos',
        model=Video,
    )


class CategoryListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'base.manage_curriculum'
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'


class CategoryDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'base.manage_curriculum'
    model = Category
    template_name = 'categories/detail.html'
    context_object_name = 'category'


class CategoryDeleteView(PermissionRequiredMixin, NeoDeleteView):
    permission_required = 'base.manage_curriculum'
    model = Category
    template_name = 'categories/delete.html'
    success_url = reverse_lazy('categories:list')
    context_object_name = 'category'


class CategoryUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'base.manage_curriculum'
    model = Category
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')
    form_class = CategoryForm


class CategoryCreateView(PermissionRequiredMixin, NeoCreateView):
    permission_required = 'base.manage_curriculum'
    model = Category
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')
    form_class = CategoryForm
