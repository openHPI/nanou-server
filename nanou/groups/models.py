from __future__ import unicode_literals

from django.urls import reverse
from py2neo.ogm import Property

from neo.models import NeoModel, NeoRelatedFrom, NeoRelatedTo


class Group(NeoModel):
    name = Property()
    required_by_videos = NeoRelatedFrom('videos.models.Video', 'REQUIRES_GROUP')
    contained_videos = NeoRelatedTo('videos.models.Video', 'CONTAINS')

    def get_absolute_url(self):
        return reverse('groups:detail', args=[self.id])
