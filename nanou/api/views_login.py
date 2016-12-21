from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from socialusers.models import SocialUser


class LoginProvidersView(View):
    providers = {  # display_name: backend_name
        'hpi': 'hpi-openid',
        # 'google': 'google-oauth2',
    }

    def get(self, request):
        return JsonResponse({
            'data': {
                name: request.build_absolute_uri(reverse('social:begin', kwargs={'backend': backend}))
                for name, backend in self.providers.items()
            },
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
