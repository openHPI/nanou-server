import json

from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from neo.utils import NeoGraph, get_neo_object_or_404
from socialusers.models import SocialUser
from videos.models import Video


@permission_required('nanou.consume_curriculum', raise_exception=True)
def next_videos(request):
    socialuser = SocialUser.user_for_django_user(request.user.id)
    return JsonResponse([video.name for video in socialuser.next_videos()], safe=False)


@csrf_exempt
@require_POST
@permission_required('nanou.consume_curriculum', raise_exception=True)
def watched_videos(request):
        video_ids = json.loads(request.body).get('videos')
        if video_ids and type(video_ids) == list and len(video_ids) > 0:
            socialuser = SocialUser.user_for_django_user(request.user.id)
            with NeoGraph() as graph:
                for video_id in video_ids:
                    video = get_neo_object_or_404(Video, int(video_id), graph)
                    socialuser.watched_videos.add(video)
                graph.push(socialuser)
                return HttpResponse()
        else:
            return HttpResponseBadRequest()
