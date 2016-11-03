from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from social.apps.django_app.default.models import UserSocialAuth

from neo.utils import NeoGraph
from socialusers.models import SocialUser


@receiver(post_save, sender=UserSocialAuth, dispatch_uid='create_neo_socialuser')
def create_neo_socialuser(sender, **kwargs):
    if kwargs.get('created', False):
        instance = kwargs.get('instance')

        group = Group.objects.get(name='Social users')
        instance.user.groups.add(group)

        user = SocialUser()
        user.user_id = instance.user_id
        with NeoGraph() as graph:
            graph.create(user)
