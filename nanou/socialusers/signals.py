from django.db.models.signals import post_save
from django.dispatch import receiver
from social.apps.django_app.default.models import UserSocialAuth

from neo.utils import NeoGraph
from socialusers.models import SocialUser


@receiver(post_save, sender=UserSocialAuth)
def create_neo_socialuser(sender, **kwargs):
    if kwargs.get('created', False):
        user = SocialUser()
        user.user_id = kwargs.get('instance').user_id
        with NeoGraph() as graph:
            graph.create(user)
