from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from py2neo.ogm import Property

from categories.models import Category
from neo.models import NeoModel, NeoRelatedTo
from neo.utils import NeoGraph
from socialusers.properties import WATCHED_DEFAULT_PROPS, PREFERENCE_DEFAULT_PROPS
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

    def next_videos(self):
        return self.next_videos_preferences()

    def next_videos_without_preferences(self):
        with NeoGraph() as graph:
            cursor = graph.run('''
                START u=node({user_id})
                MATCH (v1:Video)-[:REQUIRES_VIDEO|REQUIRES_GROUP|CONTAINS*0..]->(v2:Video)
                WITH v1, u, none(x in COLLECT(DISTINCT v2) WHERE NOT (x)<-[:WATCHED]-(u) AND v1 <> x) as deps
                WHERE deps AND NOT (v1)<-[:WATCHED]-(u)
                RETURN v1
                ORDER BY tostring(v1.name);
            ''', {
                'user_id': self.id,
            })
            return [Video.wrap(d['v1']) for d in cursor.data()]


    def next_videos_preferences(self, return_count=1):
        with NeoGraph() as graph:
            cursor = graph.run('''
                START u=node({user_id})
                MATCH (v1:Video)-[:REQUIRES_VIDEO|REQUIRES_GROUP|CONTAINS*0..]->(v2:Video)
                OPTIONAL MATCH (u)-[pref:HAS_PREFERENCE]->(cat:Category)<-[belongs:BELONGS_TO]-(v1)
                WITH v1, u, none(x in COLLECT(DISTINCT v2) WHERE NOT (x)<-[:WATCHED]-(u) AND v1 <> x) as deps, AVG(toFloat(coalesce(belongs.weight,0)) * toFloat(coalesce(pref.weight,0))) as weight
                WHERE deps AND NOT (v1)<-[:WATCHED]-(u)
                RETURN v1, weight
                ORDER BY weight DESC, tostring(v1.name)
            ''', {
                'user_id': self.id,
            })
            objects = []
            last_weight = -1
            while cursor.forward():
                node, weight = cursor.current()['v1'], cursor.current()['weight']
                if weight < last_weight and len(objects) >= return_count:
                    break
                last_weight = weight
                objects.append(Video.wrap(node))
            return objects


    def ensure_preferences(self):
        for category in Category.all():
            if category not in self.preferences:
                self.preferences.add(category, PREFERENCE_DEFAULT_PROPS)
        with NeoGraph() as graph:
            graph.push(self)
