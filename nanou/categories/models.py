from __future__ import unicode_literals

from django.urls import reverse
from py2neo.ogm import Property

from neo.models import NeoModel, NeoRelatedFrom
from socialusers.modells import PREFERENCE_DEFAULT_PROPS


class Category(NeoModel):
    name = Property()
    videos = NeoRelatedFrom('videos.models.Video', 'BELONGS_TO')
    users = NeoRelatedFrom('socialusers.models.SocialUser', 'HAS_PREFERENCE', default_props=PREFERENCE_DEFAULT_PROPS)

    def get_absolute_url(self):
        return reverse('categories:detail', args=[self.id])
