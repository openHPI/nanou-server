from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from py2neo.ogm import Property

from neo.models import NeoModel, NeoRelatedTo
from neo.utils import NeoGraph
from socialusers.properties import PREFERENCE_DEFAULT_PROPS, WATCHED_DEFAULT_PROPS
from videos.models import Video


class SocialUser(NeoModel):
    user_id = Property()
    watched_videos = NeoRelatedTo('videos.models.Video', 'WATCHED', default_props=WATCHED_DEFAULT_PROPS)
    preferences = NeoRelatedTo('categories.models.Category', 'HAS_PREFERENCE', default_props=PREFERENCE_DEFAULT_PROPS)

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

    @classmethod
    def next_videos(cls, user_id):
        return cls.next_videos_preferences(user_id)

    @classmethod
    def next_videos_preferences(cls, user_id, limit=1):
        with NeoGraph() as graph:
            cursor = graph.run('''
                MATCH (u:SocialUser{user_id:{user_id}})
                MATCH (v1:Video)-[:REQUIRES_VIDEO|REQUIRES_GROUP|CONTAINS*0..]->(v2:Video)
                MATCH (u)-[:WATCHED]->(vw:Video)
                WITH v1, v2, u, COLLECT(DISTINCT vw) as watchedV
                WITH v1, u, watchedV, none(x in COLLECT(DISTINCT v2) WHERE NOT x in watchedV AND v1 <> x) as deps
                WHERE deps AND NOT v1 in watchedV
                MATCH (cat:Category)
                OPTIONAL MATCH (u)-[pref:HAS_PREFERENCE]->(cat)
                OPTIONAL MATCH (u)-[w:WATCHED]->(v:Video)-[b:BELONGS_TO]->(cat)
                WHERE w.rating >= 0
                WITH v1, toFloat(coalesce(max(pref.weight), 0)) as prefw, toFloat(coalesce(AVG(toFloat(w.rating) * toFloat(b.weight)), 1)) as ratew
                WITH v1, prefw * ratew as weight
                RETURN v1, weight
                ORDER BY weight DESC, tostring(v1.name)
                LIMIT {limit}
            ''', {
                'user_id': user_id,
                'limit': limit,
            })

            return [Video.wrap(d['v1']) for d in cursor.data()]


    @classmethod
    def watch_history(cls, user_id):
        with NeoGraph() as graph:
            cursor = graph.run('''
                MATCH (u:SocialUser{user_id:{user_id}})
                MATCH (u)-[w:WATCHED]->(v:Video)
                RETURN DISTINCT v, w.date
                ORDER BY w.date DESC;
            ''', {
                'user_id': user_id,
            })
            return [Video.wrap(d['v']) for d in cursor.data()]

    @property
    def has_initialized_preferences(self):
        return len(self.preferences) > 0
