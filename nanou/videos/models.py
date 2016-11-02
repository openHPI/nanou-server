from __future__ import unicode_literals

from py2neo.ogm import Property, RelatedFrom, RelatedTo
from neo.models import NeoModel


class Video(NeoModel):
    name = Property()
    required_by_videos = RelatedFrom('videos.models.Video', 'REQUIRES_VIDEO')
    required_videos = RelatedTo('videos.models.Video', 'REQUIRES_VIDEO')
    required_groups = RelatedTo('groups.models.Group', 'REQUIRES_GROUP')
    contained_in_groups = RelatedFrom('groups.models.Group', 'CONTAINS')
    watched_by = RelatedFrom('socialusers.models.SocialUser', 'WATCHED')
