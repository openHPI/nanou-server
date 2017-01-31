from __future__ import unicode_literals

from django.urls import reverse
from py2neo.ogm import Property

from neo.models import NeoModel, NeoRelatedFrom, NeoRelatedTo
from socialusers.properties import WATCHED_DEFAULT_PROPS
from videos.properties import CATEGORY_DEFAULT_PROPS


class Video(NeoModel):
    name = Property()
    url = Property()
    stream_url = Property()
    image_url = Property()
    provider_name = Property()
    required_by_videos = NeoRelatedFrom('videos.models.Video', 'REQUIRES_VIDEO')
    required_videos = NeoRelatedTo('videos.models.Video', 'REQUIRES_VIDEO')
    required_groups = NeoRelatedTo('groups.models.Group', 'REQUIRES_GROUP')
    contained_in_groups = NeoRelatedFrom('groups.models.Group', 'CONTAINS')
    watched_by = NeoRelatedFrom('socialusers.models.SocialUser', 'WATCHED', default_props=WATCHED_DEFAULT_PROPS)
    categories = NeoRelatedTo('categories.models.Category', 'BELONGS_TO', default_props=CATEGORY_DEFAULT_PROPS)

    def get_absolute_url(self):
        return reverse('videos:detail', args=[self.id])
