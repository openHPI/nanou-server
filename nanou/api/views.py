from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import PreferenceSerializer, VideoSerializer
from categories.models import Category
from neo.utils import NeoGraph
from socialusers.models import SocialUser
from videos.models import Video


class NextVideosView(APIView):
    resource_name = 'videos'

    def get(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        next_videos = socialuser.next_videos()
        serializer = VideoSerializer(next_videos, many=True)
        return Response(serializer.data)


class WatchVideoView(APIView):
    resource_name = 'videos'

    def post(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        with NeoGraph() as graph:
            video = Video.select(graph, request.data['id']).first()
            if not video:
                content = {
                    'title': 'Found non-existing video id',
                    'id': request.data['id'],
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if video in socialuser.watched_videos:
                return Response({'meta': {'count': 0}})

            socialuser.watched_videos.add(video)
            graph.push(socialuser)
            return Response({'meta': {'count': 1}})


class PreferencesView(APIView):
    resource_name = 'preferences'

    def get(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        serializer = PreferenceSerializer(list(Category.all()), many=True, context={'socialuser': socialuser})
        return Response(serializer.data)

    def post(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        updates = request.data.get('updates')
        if not updates or not isinstance(updates, list):
            content = {'title': 'Found no preference updates'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if not self.validate_updates(updates):
            content = {'title': 'Invalid preference updates'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        categories, error = self.parse_updates(updates)
        if categories is None:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        for category, attributes in categories:
            socialuser.preferences.update(category, attributes)
        with NeoGraph() as graph:
            graph.push(socialuser)
        return Response({'meta': {'count': len(updates)}})

    def validate_updates(self, updates):
        return all(
            update.get('id') and update.get('attributes') and update.get('attributes').get('weight')
            for update in updates
        )

    def parse_updates(self, updates):
        objects = []
        with NeoGraph() as graph:
            for update in updates:
                category = Category.select(graph, int(update.get('id'))).first()
                if category is None:
                    return None, {
                        'title': 'Found non-existing category id',
                        'id': update.get('id'),
                    }
                objects.append((category, update.get('attributes')))
        return objects, {}
