from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required('nanou.manage_curriculum')
def landingpage(request):
    return render(request, 'landingpage.html')
