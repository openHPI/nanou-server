import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from py2neo.types import PropertyDict

from api.serializers import PreferenceSerializer, VideoSerializer, HistoryVideoSerializer, SurveySerializer
from categories.models import Category
from neo.utils import NeoGraph
from socialusers.models import SocialUser
from surveys.models import Survey
from videos.models import Video


class NextVideosView(APIView):
    resource_name = 'videos'

    def get(self, request):
        next_videos_with_weights = SocialUser.next_videos(request.user.id)
        next_videos = [d[0] for d in next_videos_with_weights]
        serializer = VideoSerializer(next_videos, many=True)

        # track suggested videos
        now = datetime.datetime.now().isoformat()
        socialuser = SocialUser.user_for_django_user(request.user.id)
        with NeoGraph() as graph:
            for video, weight in next_videos_with_weights:
                graph.run('''
                    MATCH (u:SocialUser{id:{user_id}}), (v:Video{id:{video_id}})
                    CREATE (v)-[:WAS_SUGGESTED{weight: {weight}, date: {date}}]->(u)
                ''', {
                    'user_id': socialuser.id,
                    'video_id': video.id,
                    'weight': weight,
                    'date': now,
                })
        return Response(serializer.data)


class WatchVideoView(APIView):
    resource_name = 'watches'

    def post(self, request):
        socialuser = SocialUser.user_for_django_user(request.user.id)
        with NeoGraph() as graph:
            video_id = request.data.get('video_id')
            if not video_id:
                content = {
                    'title': 'Missing video id',
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            date = request.data.get('date')
            progress = request.data.get('progress')
            rating = request.data.get('rating')
            if not all(value is not None for value in [date, progress, rating]):
                content = {
                    'title': 'Invalid attributes',
                    'id': video_id,
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            video = Video.select(graph, int(video_id)).first()
            if not video:
                content = {
                    'title': 'Found non-existing video id',
                    'id': video_id,
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            graph.run('''
                MATCH (u:SocialUser{id:{user_id}}), (v:Video{id:{video_id}})
                CREATE (u)-[:WATCHED{rating: {rating}, progress: {progress}, date: {date}}]->(v)
            ''', {
                'user_id': socialuser.id,
                'video_id': video.id,
                'rating': rating,
                'date': date,
                'progress': progress,
            })
            return Response(status=status.HTTP_204_NO_CONTENT)


class WatchHistoryView(APIView):
    resource_name = 'history'

    def get(self, request):
        watched_videos, context_data = SocialUser.watch_history(request.user.id)
        serializer = HistoryVideoSerializer(watched_videos, many=True, context=context_data)
        return Response(serializer.data)


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
        return Response(status=status.HTTP_204_NO_CONTENT)

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


class SurveyView(APIView):
    resource_name = 'surveys'

    def get(self, request):
        watch_count = SocialUser.watch_count(request.user.id)
        survey = Survey.objects.exclude(watch_minimum__gt=watch_count).order_by('watch_minimum').last()
        use_secondary = False
        if survey:
            old_uncompleted_surveys = Survey.objects.filter(watch_minimum__lt=survey.watch_minimum).exclude(completed_by=request.user)
            use_secondary = len(old_uncompleted_surveys) > 0
        serializer = SurveySerializer(survey, context={'use_secondary': use_secondary})
        return Response(serializer.data)


class SurveyCompleteView(APIView):
    resource_name = 'surveys'

    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        survey.completed_by.add(request.user)
        survey.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
