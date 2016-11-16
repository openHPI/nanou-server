from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from py2neo.ogm import Property

from neo.models import NeoModel, NeoRelatedTo
from neo.utils import NeoGraph
from videos.models import Video, WATCHED_DEFAULT_PROPS


class SocialUser(NeoModel):
    user_id = Property()
    watched_videos = NeoRelatedTo('videos.models.Video', 'WATCHED', default_props=WATCHED_DEFAULT_PROPS)

    def get_absolute_url(self):
        return reverse('socialusers:detail', args=[self.id])

    @classmethod
    def user_for_django_user(cls, dj_id):
        with NeoGraph() as graph:
            obj = cls.select(graph).where('_.user_id = {}'.format(dj_id)).first()
            if obj is None:
                raise Http404(_('No %(verbose_name)s found matching the query') %
                              {'verbose_name': cls.__name__})
            return obj

    def next_videos(self):
        with NeoGraph() as graph:
            cursor = graph.run('''
                START u=node({user_id})
                MATCH (v1:Video)-[:REQUIRES_VIDEO|REQUIRES_GROUP|CONTAINS*0..]->(v2:Video)
                WITH v1, u, none(x in COLLECT(DISTINCT v2) WHERE NOT (x)<-[:WATCHED]-(u) AND v1 <> x) as deps
                WHERE deps AND NOT (v1)<-[:WATCHED]-(u)
                RETURN v1
                ORDER BY tostring(v1.name);
            ''', {
                'user_id': self.id
            })
            return [Video.wrap(d['v1']) for d in cursor.data()]
