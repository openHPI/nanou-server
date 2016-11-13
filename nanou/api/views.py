from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import VideoSerializer
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
