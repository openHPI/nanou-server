from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from social.apps.django_app.default.models import UserSocialAuth

from neo.utils import NeoGraph
from socialusers.models import SocialUser


@receiver(post_save, sender=UserSocialAuth, dispatch_uid='setup_social_auth_user')
def setup_social_auth_user(sender, **kwargs):
    if kwargs.get('created', False):
        instance = kwargs.get('instance')

        if instance:
            group = Group.objects.get(name='Social users')
            instance.user.groups.add(group)

            create_neo_socialuser(instance.user_id)

def create_neo_socialuser(user_id):
    user = SocialUser()
    with NeoGraph() as graph:
        tx = graph.begin()
        user.id = tx.run('MATCH (n:{}) RETURN COUNT(n)+1'.format(SocialUser.__primarylabel__)).evaluate()
        user.user_id = user_id
        tx.create(user)
        tx.commit()
