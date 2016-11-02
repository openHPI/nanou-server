from __future__ import unicode_literals

from django.apps import AppConfig


class SocialUsersConfig(AppConfig):
    name = 'socialusers'

    def ready(self):
        import socialusers.signals  # noqa
