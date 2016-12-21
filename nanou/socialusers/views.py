from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from categories.models import Category
from neo.forms import NeoForm, NeoRelationshipField
from neo.utils import NeoGraph
from neo.views import NeoDetailView, NeoListView, NeoUpdateView
from neoextras.views import NeoRelationshipUpdateView
from socialusers.models import SocialUser
from videos.models import Video


class SocialUserForm(NeoForm):
    watched_videos = NeoRelationshipField(
        label='Watched videos',
        model=Video,
    )
    preferences = NeoRelationshipField(
        label='Preferences',
        model=Category,
    )


class SocialUserListView(PermissionRequiredMixin, NeoListView):
    permission_required = 'base.manage_curriculum'
    model = SocialUser
    template_name = 'socialusers/list.html'
    context_object_name = 'socialusers'


class SocialUserDetailView(PermissionRequiredMixin, NeoDetailView):
    permission_required = 'base.manage_curriculum'
    model = SocialUser
    template_name = 'socialusers/detail.html'
    context_object_name = 'socialuser'


class SocialUserUpdateView(PermissionRequiredMixin, NeoUpdateView):
    permission_required = 'base.manage_curriculum'
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


class SocialUserHasPreferenceView(PermissionRequiredMixin, NeoRelationshipUpdateView):
    permission_required = 'base.manage_curriculum'
    start_model = SocialUser
    end_model = Category
    relationship_name = 'HAS_PREFERENCE'


class SocialUserWatchedView(PermissionRequiredMixin, NeoRelationshipUpdateView):
    permission_required = 'base.manage_curriculum'
    start_model = SocialUser
    end_model = Video
    relationship_name = 'WATCHED'
