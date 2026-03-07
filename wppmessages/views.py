from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from .forms import MessageForm
from utils.evoapi import send_text_message


@login_required
def messages_manager(request):
    return render(request, 'messages_manager.html', {'form': MessageForm()})


@csrf_exempt
@require_http_methods(["POST"])
def hook(request):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    if client_ip != settings.EVOLUTION_SERVER_IP:
        return HttpResponseForbidden('Forbidden')
    body_string = request.body.decode('utf-8')
    send_text_message('5545998231771', str(body_string))
    return HttpResponse('OK')
