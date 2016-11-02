from socialusers.models import SocialUser

from neo.tests import NeoTestCase


class SocialUserTests(NeoTestCase):
    fixtures = ['socialusers_testdata']

    def test_creation(self):
        all_socialusers = SocialUser.all()
        self.assertEqual(len(list(all_socialusers)), 1)
