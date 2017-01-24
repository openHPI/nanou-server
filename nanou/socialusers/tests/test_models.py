from social_django.models import UserSocialAuth

from neo.tests import NeoTestCase
from socialusers.models import SocialUser


class SocialUserTests(NeoTestCase):
    fixtures = ['users_testdata']

    def test_creation(self):
        pre_socialuser_count = len(list(SocialUser.all()))
        UserSocialAuth.objects.create(user_id=2)
        post_socialuser_count = len(list(SocialUser.all()))
        self.assertEqual(pre_socialuser_count+1, post_socialuser_count)
