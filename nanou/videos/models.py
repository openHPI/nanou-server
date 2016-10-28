from __future__ import unicode_literals

from py2neo.ogm import Property, RelatedFrom, RelatedTo
from neo.models import NeoModel


class Video(NeoModel):
    name = Property()

    required_by_videos = RelatedFrom('Video', 'REQUIRES_VIDEO')
    required_videos = RelatedTo('Video', 'REQUIRES_VIDEO')
