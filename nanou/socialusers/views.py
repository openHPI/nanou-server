from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views import View

from nanou.widgets import SemanticUISelectMultiple
from neo.forms import NeoForm
from neo.utils import NeoGraph
from neo.views import NeoListView, NeoDetailView, NeoUpdateView
from videos.models import Video

from .models import SocialUser


class SocialUserForm(NeoForm):
    wathed_videos = forms.MultipleChoiceField(
        label='Watched videos',
        choices=[(video.id, video.name) for video in Video.all()],
        required=False,
        widget=SemanticUISelectMultiple(),
    )


class SocialUserListView(LoginRequiredMixin, NeoListView):
    model = SocialUser
    template_name = 'socialusers/list.html'
    context_object_name = 'socialusers'


class SocialUserDetailView(LoginRequiredMixin, NeoDetailView):
    model = SocialUser
    template_name = 'socialusers/detail.html'
    context_object_name = 'socialuser'


class SocialUserUpdateView(LoginRequiredMixin, NeoUpdateView):
    model = SocialUser
    template_name = 'socialusers/form.html'
    success_url = reverse_lazy('socialusers:list')
    form_class = SocialUserForm

    def get_context_data(self, **kwargs):
        context = super(SocialUserUpdateView, self).get_context_data(**kwargs)
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            obj = SocialUser.select(graph, pk).first()
            context['user_id'] = obj.user_id
        return context


class LoggedInView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponse('Successfully authenticated.')
        else:
            return HttpResponseForbidden('Authentication failed.')
