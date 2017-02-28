from datetime import datetime

from django.contrib.auth.models import Group, User
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from socialusers.models import SocialUser
from socialusers.signals import create_neo_socialuser


class LoginProvidersView(View):
    providers = [  # (display_name, backend_name)
        ('openHPI', 'openhpi'),
        # ('google', 'google-oauth2'),
        ('facebook', 'facebook'),
    ]

    def get(self, request):
        return JsonResponse({
            'data': [
                [name, request.build_absolute_uri(reverse('social:begin', kwargs={'backend': backend}))]
                for name, backend in self.providers
            ],
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

class TestLoginView(View):
    def get(self, request):
        vendor_id = request.GET.get('vendorId')
        if vendor_id is None:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, reason='No vendor id')

        try:
            user = User.objects.get(username=vendor_id)
        except User.DoesNotExist:
            user = User.objects.create_user(vendor_id)
            group = Group.objects.get(name='Social users')
            user.groups.add(group)
            user.save()
            create_neo_socialuser(user.id)

        token, _ = Token.objects.get_or_create(user=user)
        socialuser = SocialUser.user_for_django_user(user.id)

        return JsonResponse({
            'authenticated': True,
            'preferencesInitialized': socialuser.has_initialized_preferences,
            'token': token.key,
        })


class CombineAccountsView(APIView):
    def get(self, request):
        vendor_id = request.GET.get('vendorId')
        if vendor_id is None:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, reason='No vendor id')
        try:
            vendor_user = User.objects.get(username=vendor_id)
        except User.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, reason='Invalid vendor id')

        if vendor_user == request.user:
            # you can't combine with yourself
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, reason='Unable to combine')

        socialuser = SocialUser.user_for_django_user(vendor_user.id)
        socialuser.user_id = request.user.id
        socialuser.save()

        vendor_user.username = '%s#%s' % (datetime.now().strftime('%Y%M%d-%H%m%S-%s'), vendor_user.username)
        vendor_user.save()

        request.user.username = vendor_id
        request.user.save()

        return Response(status=status.HTTP_201_CREATED)
