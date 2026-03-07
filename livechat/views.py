from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def livechat(request):
    return render(request, 'livechat.html')
