from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from surveys.models import Survey


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = (
            'link',
            'secondary_link',
            'watch_minimum',
        )


class SurveyListView(PermissionRequiredMixin, ListView):
    permission_required = 'base.manage_curriculum'
    model = Survey
    template_name = 'survey/list.html'
    context_object_name = 'surveys'


class SurveyDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'base.manage_curriculum'
    model = Survey
    template_name = 'survey/detail.html'
    context_object_name = 'survey'


class SurveyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'base.manage_curriculum'
    model = Survey
    template_name = 'survey/delete.html'
    success_url = reverse_lazy('surveys:list')
    context_object_name = 'survey'


class SurveyUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'base.manage_curriculum'
    model = Survey
    template_name = 'survey/form.html'
    success_url = reverse_lazy('surveys:list')
    form_class = SurveyForm


class SurveyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'base.manage_curriculum'
    model = Survey
    template_name = 'survey/form.html'
    success_url = reverse_lazy('surveys:list')
    form_class = SurveyForm
