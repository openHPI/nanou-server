from __future__ import unicode_literals

from django.urls import reverse
from py2neo.ogm import Property, RelatedFrom, RelatedTo

from neo.models import NeoModel


class Group(NeoModel):
    name = Property()
    required_by_videos = RelatedFrom('videos.models.Video', 'REQUIRES_GROUP')
    contained_videos = RelatedTo('videos.models.Video', 'CONTAINS')

    def get_absolute_url(self):
        return reverse('groups:detail', args=[self.id])
