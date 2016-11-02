from __future__ import unicode_literals

from py2neo.ogm import Property, RelatedTo
from neo.models import NeoModel


class SocialUser(NeoModel):
    __primarykey__ = 'user_id'

    user_id = Property()
    wathed_videos = RelatedTo('videos.models.Video', 'WATCHED')
