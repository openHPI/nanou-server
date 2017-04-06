from __future__ import unicode_literals

from datetime import datetime

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
                OPTIONAL MATCH (u)-[hasWatched:WATCHED]->(videosW:Video)
                WHERE hasWatched.progress > 0
                WITH COLLECT(DISTINCT videosW) as videosWatched
                MATCH (u:SocialUser{user_id:{user_id}})
                OPTIONAL MATCH (u)-[hasDismissed:WATCHED]->(videosSkiped:Video)
                WHERE hasDismissed.progress = 0 AND hasDismissed.date STARTS WITH {today}
                WITH videosWatched, COLLECT(DISTINCT videosSkiped) as videosSkipedToday
                MATCH (v1:Video)-[:REQUIRES_VIDEO|REQUIRES_GROUP|CONTAINS*0..]->(v2:Video)
                WITH v1, videosWatched, videosSkipedToday, none(x in COLLECT(DISTINCT v2) WHERE NOT x in videosWatched AND v1 <> x) as deps
                WHERE deps AND NOT v1 in videosWatched AND NOT v1 in videosSkipedToday
                MATCH (u:SocialUser{user_id:{user_id}})
                OPTIONAL MATCH (cat:Category)
                OPTIONAL MATCH (u)-[pref:HAS_PREFERENCE]->(cat)
                OPTIONAL MATCH (u)-[w:WATCHED]->(v:Video)-[b:BELONGS_TO]->(cat)
                WHERE w.rating >= 0
                WITH v1, cat, toFloat(coalesce(max(pref.weight), 0.5)) as prefw, toFloat(coalesce(AVG(toFloat(w.rating) * toFloat(b.weight)), 1)) as ratew
                WITH v1, cat, prefw * ratew as catWeight
                OPTIONAL MATCH (v1)-[belongs:BELONGS_TO]->(cat)
                WITH v1, toFloat(AVG(coalesce(belongs.weight, 0.1) * catWeight)) as weight
                OPTIONAL MATCH (v3:Video)-[:REQUIRES_VIDEO]->(v1)
                RETURN v1, weight, COUNT(DISTINCT v3) as dep_count
                ORDER BY weight DESC, tostring(v1.name)
                LIMIT {limit}
            ''', {
                'user_id': user_id,
                'today': datetime.now().isoformat()[:10],  # returns date with format 'YYYY-MM-DD'
                'limit': limit,
            })

            data = [(Video.wrap(d['v1']), d['weight'], d['dep_count']) for d in cursor.data()]
            videos = [d[0] for d in data]
            context = {d[0].id: {
                'weigth': d[1],
                'dep_count': d[2],
            } for d in data}
            return videos, context

    @classmethod
    def watch_history(cls, user_id):
        with NeoGraph() as graph:
            cursor = graph.run('''
                MATCH (u:SocialUser{user_id:{user_id}})-[w:WATCHED]->(v:Video)
                WHERE w.progress > 0
                RETURN DISTINCT v, MAX(w.date) as date, COUNT(w) as count, MAX(w.progress) as progress
                ORDER BY date DESC
            ''', {
                'user_id': user_id,
            })
            data = [(Video.wrap(d['v']), d['date'], d['count'], d['progress']) for d in cursor.data()]
            videos = [d[0] for d in data]
            context = {d[0].id: d[1:] for d in data}
            return videos, context

    @classmethod
    def watch_count(cls, user_id):
        with NeoGraph() as graph:
            cursor = graph.run('''
                MATCH (u:SocialUser{user_id:{user_id}})-[w:WATCHED]->(v:Video)
                WHERE w.progress > 0
                RETURN COUNT(DISTINCT v) as count
            ''', {
                'user_id': user_id,
            })
            data = cursor.data()
            if not isinstance(data, list):
                return 0
            if len(data) == 0:
                return 0
            count = data[0].get('count')
            if not isinstance(count, int):
                return 0
            return count

    @property
    def has_initialized_preferences(self):
        return len(self.preferences) > 0
