from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

import base.statistics as statistics
from groups.models import Group
from socialusers.models import SocialUser
from videos.models import Video


@permission_required('base.manage_curriculum')
def landingpage(request):
    user_ids = [s.user_id for s in SocialUser.all()]
    return render(request, 'landingpage.html', {
        'video_count': len(list(Video.all())),
        'group_count': len(list(Group.all())),
        'socialuser_count': len(set(user_ids)),
        'socialuser_all_count': len(user_ids),
        'overall_suggestions_count': statistics.overall_suggestions_count(),
        'overall_suggestions_user_count': statistics.overall_suggestions_user_count(),
        'suggestions_user_count': statistics.suggestions_user_count(),
        'overall_watch_count': statistics.overall_watch_count(),
        'overall_watch_user_count': statistics.overall_watch_user_count(),
        'watch_user_count': statistics.watch_user_count(),
        'overall_dismiss_count': statistics.overall_dismiss_count(),
        'overall_dismiss_user_count': statistics.overall_dismiss_user_count(),
        'dismiss_user_count': statistics.dismiss_user_count(),
        'user_watches': statistics.user_watches(),
    })
