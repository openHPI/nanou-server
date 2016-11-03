from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from neo.utils import NeoGraph, get_neo_object_or_404
from socialusers.models import SocialUser
from videos.models import Video


@permission_required('nanou.consume_curriculum', raise_exception=True)
def next_videos(request):
    socialuser = SocialUser.user_for_django_user(request.user.id)
    return JsonResponse([video.name for video in socialuser.next_videos()], safe=False)


@require_POST
@permission_required('nanou.consume_curriculum', raise_exception=True)
def watched_video(request, video_id):
    with NeoGraph() as graph:
        video = get_neo_object_or_404(Video, int(video_id), graph)
        socialuser = SocialUser.user_for_django_user(request.user.id)
        socialuser.watched_videos.add(video)
        graph.push(socialuser)
        return HttpResponse()
