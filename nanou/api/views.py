from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from neo.utils import NeoGraph, get_neo_object_or_404
from socialusers.models import SocialUser
from videos.models import Video


class NextVideosView(APIView):
    def get(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        return Response({
            'data': [video.name for video in socialuser.next_videos()],
        })


class WatchVideosView(APIView):
    def post(self, request):
        video_ids = request.data.get('videos', [])
        if not isinstance(video_ids, list) or len(video_ids) == 0:
            content = {'error': {'videos': 'Require non-empty list of video ids'}}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            socialuser = SocialUser.user_for_django_user(request.user.id)
            with NeoGraph() as graph:
                for video_id in video_ids:
                    video = get_neo_object_or_404(Video, int(video_id), graph)
                    socialuser.watched_videos.add(video)
                graph.push(socialuser)
                return Response({'meta': {'watch_video_count': len(video_ids)}})
        except Http404:
            content = {'error': {'videos': 'Found non-existing video ids'}}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
