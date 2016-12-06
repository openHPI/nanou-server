from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.models import Category
from neo.forms import NeoForm, NeoRelationshipField
from neo.utils import NeoGraph
from neo.views import NeoDetailView, NeoListView, NeoUpdateView
from neoextras.views import NeoRelationshipUpdateView
from videos.models import Video

from .models import SocialUser


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


class LoginProvidersView(APIView):
    permission_classes = (AllowAny,)
    providers = {  # display_name: backend_name
        'hpi': 'hpi-openid',
        # 'google': 'google-oauth2',
    }

    def get(self, request):
        return Response({
            name: reverse('social:begin', kwargs={'backend': backend})
            for name, backend in self.providers.items()
        })


class AuthStatusView(View):
    def get(self, request):
        rest_request = Request(request)
        try:
            user_token = TokenAuthentication().authenticate(rest_request)
            if user_token is None:
                raise AuthenticationFailed
            user, token = user_token
        except AuthenticationFailed:
            try:
                user_session = SessionAuthentication().authenticate(rest_request)
                if user_session is None:
                    raise AuthenticationFailed
                user, _ = user_session
                if not user.has_perm('base.consume_curriculum'):
                    raise AuthenticationFailed
                token, _ = Token.objects.get_or_create(user=user)
            except AuthenticationFailed:
                return JsonResponse({
                    'authenticated': False,
                })
        socialuser = SocialUser.user_for_django_user(user.id)
        return JsonResponse({
            'authenticated': True,
            'preferencesInitialized': socialuser.has_initialized_preferences,
            'token': token.key,
        })
