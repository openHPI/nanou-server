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
        next_videos = SocialUser.next_videos(request.user.id)
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

            date = request.data.get('date')
            progress = request.data.get('progress')
            rating = request.data.get('rating')

            if not all([date, progress, rating]):
                content = {
                    'title': 'Invalid attributes',
                    'id': request.data['id'],
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            properties = {
                'date': date,
                'progress': progress,
                'rating': rating,
            }
            socialuser.watched_videos.add(video, properties)
            graph.push(socialuser)
            return Response({'meta': {'count': 1}})


class PreferencesView(APIView):
    resource_name = 'preferences'

    def get(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        categories = sorted(Category.all(), key=lambda c: c.name.lower())
        serializer = PreferenceSerializer(categories, many=True, context={'socialuser': socialuser})
        return Response(serializer.data)


class PreferencesUpdateView(APIView):
    resource_name = 'preferences'

    def patch(self, request, pk):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        category, error = self.parse_update(pk)
        if category is None:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if not self.validate_update(request.data, pk):
            content = {'title': 'Invalid preference updates'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        properties = {
            'weight': request.data.get('weight')
        }
        if category in socialuser.preferences:
            socialuser.preferences.update(category, properties)
        else:
            socialuser.preferences.add(category, properties)
        with NeoGraph() as graph:
            graph.push(socialuser)
        return Response({'meta': {'count': 1}})

    def validate_update(self, update, pk):
        return update.get('id') == pk and update.get('weight')

    def parse_update(self, pk):
        with NeoGraph() as graph:
            category = Category.select(graph, int(pk)).first()
            if category is None:
                return None, {
                    'title': 'Found non-existing category id',
                    'id': pk,
                }
            return category, {}
