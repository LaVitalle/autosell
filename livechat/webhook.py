import json
from datetime import datetime, timezone

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from contacts.models import Contact
from .models import Conversation, ChatMessage
from utils.api_response import log_system_event


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    if client_ip != settings.EVOLUTION_SERVER_IP:
        return HttpResponseForbidden('Forbidden')

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponse('Invalid JSON', status=400)

    event = payload.get('event')

    if event == 'messages.upsert':
        _handle_messages_upsert(payload)
    elif event == 'messages.update':
        _handle_messages_update(payload)

    return HttpResponse('OK')


def _handle_messages_upsert(payload):
    try:
        data = payload.get('data', {})
        key = data.get('key', {})
        remote_jid = key.get('remoteJid', '')

        if not remote_jid or '@g.us' in remote_jid:
            return

        wpp_message_id = key.get('id')
        if not wpp_message_id:
            return

        if ChatMessage.objects.filter(wpp_message_id=wpp_message_id).exists():
            return

        from_me = key.get('fromMe', False)
        direction = 'out' if from_me else 'in'

        message_data = data.get('message', {})
        text = (
            message_data.get('conversation') or
            message_data.get('extendedTextMessage', {}).get('text') or
            ''
        )

        if not text and message_data.get('imageMessage'):
            text = message_data['imageMessage'].get('caption', '[Imagem]')
        if not text:
            text = '[Mensagem]'

        phone = remote_jid.split('@')[0]

        contact, _ = Contact.objects.get_or_create(
            phone=phone,
            defaults={'name': phone}
        )

        conversation, _ = Conversation.objects.get_or_create(
            remote_jid=remote_jid,
            defaults={'contact': contact}
        )

        msg_timestamp = data.get('messageTimestamp')
        if msg_timestamp:
            try:
                ts = datetime.fromtimestamp(int(msg_timestamp), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                ts = datetime.now(tz=timezone.utc)
        else:
            ts = datetime.now(tz=timezone.utc)

        status = 'read' if from_me else 'delivered'

        ChatMessage.objects.create(
            contact=contact,
            conversation=conversation,
            remote_jid=remote_jid,
            wpp_message_id=wpp_message_id,
            direction=direction,
            msg_type='text',
            content=text,
            status=status,
            timestamp=ts,
        )

        preview = text[:200] if text else ''
        conversation.last_message_text = preview
        conversation.last_message_at = ts
        conversation.last_message_direction = direction
        if direction == 'in':
            conversation.unread_count += 1
        conversation.save()

    except Exception as e:
        log_system_event('ERROR', 'livechat.webhook.messages_upsert', str(e))


def _handle_messages_update(payload):
    try:
        data = payload.get('data', {})

        updates = data if isinstance(data, list) else [data]

        for update in updates:
            key = update.get('key', {})
            wpp_message_id = key.get('id')
            if not wpp_message_id:
                continue

            update_data = update.get('update', {})
            new_status_code = update_data.get('status')

            status_map = {2: 'sent', 3: 'delivered', 4: 'read'}
            new_status = status_map.get(new_status_code)
            if not new_status:
                continue

            ChatMessage.objects.filter(wpp_message_id=wpp_message_id).update(status=new_status)

    except Exception as e:
        log_system_event('ERROR', 'livechat.webhook.messages_update', str(e))
