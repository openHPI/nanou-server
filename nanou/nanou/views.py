from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from groups.models import Group
from socialusers.models import SocialUser
from videos.models import Video


@permission_required('nanou.manage_curriculum')
def landingpage(request):
    return render(request, 'landingpage.html', {
        'video_count': len(list(Video.all())),
        'group_count': len(list(Group.all())),
        'socialuser_count': len(list(SocialUser.all())),
    })
