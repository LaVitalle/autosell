import json
from datetime import datetime, timezone

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.db import IntegrityError
from django.db.models import Q

from contacts.models import Contact
from .models import Conversation, ChatMessage, Cart, Sale
from utils.api_response import log_system_event


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
    allowed_ips = {settings.EVOLUTION_SERVER_IP, '127.0.0.1', '::1', '172.18.0.1', '10.11.0.4'}
    if client_ip not in allowed_ips:
        log_system_event('WARNING', 'livechat.webhook', f'IP bloqueado: {client_ip}')
        return HttpResponseForbidden('Forbidden')

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        log_system_event('ERROR', 'livechat.webhook', f'JSON invalido: {request.body[:500]}')
        return HttpResponse('Invalid JSON', status=400)

    event = payload.get('event')

    # Log payload completo para debug
    log_system_event('INFO', 'livechat.webhook',
        f'Evento: {event} | Payload: {json.dumps(payload, ensure_ascii=False, default=str)}')

    if event == 'messages.upsert':
        _handle_messages_upsert(payload)
    elif event == 'messages.update':
        _handle_messages_update(payload)

    return HttpResponse('OK')


def _handle_messages_upsert(payload):
    try:
        data = payload.get('data', {})

        # Evolution API v2 pode enviar como array ou objeto direto
        # Tentar extrair a mensagem do formato correto
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict) and 'key' in data:
            messages = [data]
        elif isinstance(data, dict):
            # Pode estar em data.messages, data.message, ou outro wrapper
            messages = data.get('messages', data.get('message', [data]))
            if isinstance(messages, dict):
                messages = [messages]
        else:
            log_system_event('WARNING', 'livechat.webhook.messages_upsert',
                f'Formato data inesperado: {json.dumps(data)[:500]}')
            return

        for msg_data in messages:
            _process_single_message(msg_data)

    except Exception as e:
        log_system_event('ERROR', 'livechat.webhook.messages_upsert',
            f'{type(e).__name__}: {e} | Payload: {json.dumps(payload)[:800]}')


def _phone_variants(phone):
    """Variantes equivalentes de um telefone brasileiro para tratar o nono dígito.

    Ex.: 5545999037399 (13 dígitos, formato novo) e 554599037399 (12 dígitos sem
    o 9 móvel) representam o mesmo contato — Evolution às vezes devolve sem o 9.
    """
    if not phone or not phone.startswith('55') or len(phone) not in (12, 13):
        return [phone] if phone else []

    body = phone[4:]
    if len(phone) == 13 and body.startswith('9'):
        return [phone, phone[:4] + body[1:]]
    if len(phone) == 12 and body.startswith('9'):
        return [phone, phone[:4] + '9' + body]
    return [phone]


def _process_single_message(data):
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
    if message_data is None:
        message_data = {}

    text = (
        message_data.get('conversation') or
        message_data.get('extendedTextMessage', {}).get('text') or
        ''
    )

    msg_type = 'text'
    media_url = None

    if message_data.get('imageMessage'):
        img_msg = message_data['imageMessage']
        if not text:
            text = img_msg.get('caption', '')
        msg_type = 'image'
        media_url = _download_media(data, 'image', img_msg.get('mimetype', 'image/jpeg'))
    elif message_data.get('audioMessage'):
        audio_msg = message_data['audioMessage']
        msg_type = 'audio'
        media_url = _download_media(data, 'audio', audio_msg.get('mimetype', 'audio/ogg'))
    elif not text and message_data.get('videoMessage'):
        text = message_data['videoMessage'].get('caption', '[Video]')
    elif not text and message_data.get('documentMessage'):
        text = message_data['documentMessage'].get('fileName', '[Documento]')
    elif not text and message_data.get('stickerMessage'):
        text = '[Sticker]'
    elif not text and message_data.get('contactMessage'):
        text = '[Contato]'
    elif not text and message_data.get('locationMessage'):
        text = '[Localizacao]'

    if not text and not media_url:
        text = '[Mensagem]'

    # Dedup para mensagens fromMe=true (echo de mensagem enviada pelo nosso sistema)
    if from_me:
        from datetime import timedelta
        cutoff = datetime.now(tz=timezone.utc) - timedelta(seconds=30)
        # Busca mensagem pendente sem wpp_message_id (enviada pelo nosso sistema)
        pending_msg = ChatMessage.objects.filter(
            remote_jid=remote_jid,
            direction='out',
            content=text,
            timestamp__gte=cutoff,
            wpp_message_id__isnull=True,
        ).order_by('-timestamp').first()

        if pending_msg:
            # Echo da nossa mensagem — atualizar wpp_message_id e retornar
            pending_msg.wpp_message_id = wpp_message_id
            pending_msg.save(update_fields=['wpp_message_id'])
            return
        # Nao e echo — mensagem enviada externamente (pelo celular), continuar registrando

    lid = remote_jid.split('@')[0]

    # Extrair telefone e nome apenas de mensagens recebidas (fromMe=false)
    # Mensagens fromMe=true vem com pushName/sender da instancia, nao do contato
    phone = ''
    push_name = ''
    if not from_me:
        push_name = data.get('pushName', '').strip()
        sender_pn = key.get('senderPn', '')
        remote_jid_alt = key.get('remoteJidAlt', '')
        if sender_pn:
            phone = sender_pn.split('@')[0]
        elif remote_jid_alt:
            phone = remote_jid_alt.split('@')[0]
        elif '@s.whatsapp.net' in remote_jid:
            phone = lid

    # Cross-reference lookup: buscar por lid OU phone (tolerante ao 9° dígito)
    phone_options = _phone_variants(phone)
    contact_by_lid = Contact.objects.filter(lid=lid).first()
    contact_by_phone = Contact.objects.filter(phone__in=phone_options).first() if phone_options else None

    if contact_by_lid and contact_by_phone and contact_by_lid.id != contact_by_phone.id:
        # Conflito: lid e phone apontam para contatos diferentes — merge
        if contact_by_lid.id < contact_by_phone.id:
            primary, secondary = contact_by_lid, contact_by_phone
        else:
            primary, secondary = contact_by_phone, contact_by_lid
        _merge_contacts(primary, secondary)
        contact = primary
    elif contact_by_lid:
        contact = contact_by_lid
    elif contact_by_phone:
        contact = contact_by_phone
    else:
        # Criar novo contato (com fallback para race conditions)
        try:
            contact = Contact.objects.create(
                lid=lid, phone=phone or None,
                name=push_name or phone or lid,
            )
        except IntegrityError:
            contact = Contact.objects.filter(
                Q(lid=lid) | (Q(phone__in=phone_options) if phone_options else Q())
            ).first()
            if not contact:
                raise

    # Enriquecer contato existente
    update_fields = []
    if not contact.lid and lid:
        contact.lid = lid
        update_fields.append('lid')
    if not contact.phone and phone:
        contact.phone = phone
        update_fields.append('phone')
    if not from_me and push_name and contact.name in (lid, contact.lid, contact.phone):
        contact.name = push_name
        update_fields.append('name')
    if update_fields:
        contact.save(update_fields=update_fields)

    conversation, _ = Conversation.objects.get_or_create(
        remote_jid=remote_jid,
        defaults={'contact': contact}
    )

    msg_timestamp = data.get('messageTimestamp')
    if msg_timestamp:
        try:
            ts_val = int(str(msg_timestamp))
            ts = datetime.fromtimestamp(ts_val, tz=timezone.utc)
        except (ValueError, TypeError, OSError):
            ts = datetime.now(tz=timezone.utc)
    else:
        ts = datetime.now(tz=timezone.utc)

    status = 'sent' if from_me else 'delivered'

    ChatMessage.objects.create(
        contact=contact,
        conversation=conversation,
        remote_jid=remote_jid,
        wpp_message_id=wpp_message_id,
        direction=direction,
        msg_type=msg_type,
        content=text,
        media_url=media_url,
        status=status,
        timestamp=ts,
    )

    if text:
        preview = text[:200]
    elif msg_type == 'image':
        preview = '[Imagem]'
    elif msg_type == 'audio':
        preview = '[Audio]'
    else:
        preview = '[Mensagem]'
    conversation.last_message_text = preview
    conversation.last_message_at = ts
    conversation.last_message_direction = direction
    if direction == 'in':
        conversation.unread_count += 1
    conversation.save()


def _download_media(data, media_type, mimetype):
    """Baixa mídia do payload do webhook e armazena no MinIO.
    Tenta: 1) getBase64FromMediaMessage API  2) base64 do payload  3) mediaUrl  4) jpegThumbnail"""
    import uuid
    from utils.storage import upload_media_from_base64, upload_media_from_url
    from utils.evoapi import get_base64_from_media_message

    try:
        message_data = data.get('message', {}) or {}
        media_key = f'{media_type}Message'

        # Mapear mimetype para extensão
        ext_map = {
            'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp',
            'image/gif': '.gif',
            'audio/ogg': '.ogg', 'audio/ogg; codecs=opus': '.ogg',
            'audio/mpeg': '.mp3', 'audio/mp4': '.m4a', 'audio/aac': '.aac',
        }
        ext = ext_map.get(mimetype.split(';')[0].strip(), '.jpg' if media_type == 'image' else '.ogg')
        file_name = f'chat_media/{media_type}_{uuid.uuid4().hex[:12]}{ext}'

        # Fonte 1: Chamar Evolution API para obter base64 (mais confiável)
        # A API espera o objeto completo com key + message
        base64_data = get_base64_from_media_message(data)
        if base64_data:
            # Remover prefixo data:mimetype;base64, se presente
            if ';base64,' in base64_data:
                base64_data = base64_data.split(';base64,', 1)[1]
            log_system_event('INFO', 'livechat.webhook.download_media',
                f'Usando getBase64FromMediaMessage para {media_type}')
            return upload_media_from_base64(file_name, base64_data)

        # Fonte 2: base64 no nível raiz do payload (webhookBase64)
        base64_payload = data.get('base64')
        if base64_payload:
            if ';base64,' in base64_payload:
                base64_payload = base64_payload.split(';base64,', 1)[1]
            log_system_event('INFO', 'livechat.webhook.download_media',
                f'Usando base64 do payload para {media_type}')
            return upload_media_from_base64(file_name, base64_payload)

        # Fonte 3: mediaUrl (quando S3 configurado na Evolution)
        media_url = data.get('mediaUrl')
        if media_url:
            log_system_event('INFO', 'livechat.webhook.download_media',
                f'Usando mediaUrl para {media_type}: {media_url[:100]}')
            return upload_media_from_url(file_name, media_url)

        # Fonte 4: jpegThumbnail (fallback baixa qualidade, apenas imagens)
        if media_type == 'image':
            thumbnail = message_data.get(media_key, {}).get('jpegThumbnail')
            if thumbnail:
                log_system_event('INFO', 'livechat.webhook.download_media',
                    f'Usando jpegThumbnail como fallback para imagem')
                file_name = f'chat_media/image_{uuid.uuid4().hex[:12]}.jpg'
                return upload_media_from_base64(file_name, thumbnail)

        log_system_event('WARNING', 'livechat.webhook.download_media',
            f'Nenhuma fonte de midia disponivel para {media_type}')
        return None
    except Exception as e:
        log_system_event('ERROR', 'livechat.webhook.download_media',
            f'{type(e).__name__}: {e}')
        return None


def _merge_contacts(primary, secondary):
    """Merge secondary contact into primary. Deleta secondary."""
    from wppmessages.models import Message as WppMessage

    # Copiar campos faltantes do secondary para primary
    update_fields = []
    if not primary.lid and secondary.lid:
        primary.lid = secondary.lid
        update_fields.append('lid')
    if not primary.phone and secondary.phone:
        primary.phone = secondary.phone
        update_fields.append('phone')
    if primary.name in (primary.lid, primary.phone) and secondary.name not in (secondary.lid, secondary.phone):
        primary.name = secondary.name
        update_fields.append('name')
    if update_fields:
        primary.save(update_fields=update_fields)

    # Obter conversations
    try:
        primary_conv = Conversation.objects.get(contact=primary)
    except Conversation.DoesNotExist:
        primary_conv = None
    try:
        secondary_conv = Conversation.objects.get(contact=secondary)
    except Conversation.DoesNotExist:
        secondary_conv = None

    if secondary_conv:
        if primary_conv:
            # Mover mensagens e carts do secondary conv para primary conv
            ChatMessage.objects.filter(conversation=secondary_conv).update(
                conversation=primary_conv, contact=primary)
            Cart.objects.filter(conversation=secondary_conv).update(
                conversation=primary_conv, contact=primary)
            # Atualizar resumo se secondary e mais recente
            if (secondary_conv.last_message_at and
                (not primary_conv.last_message_at or
                 secondary_conv.last_message_at > primary_conv.last_message_at)):
                primary_conv.last_message_text = secondary_conv.last_message_text
                primary_conv.last_message_at = secondary_conv.last_message_at
                primary_conv.last_message_direction = secondary_conv.last_message_direction
            primary_conv.unread_count += secondary_conv.unread_count
            primary_conv.save()
            secondary_conv.delete()
        else:
            secondary_conv.contact = primary
            secondary_conv.save(update_fields=['contact'])

    # Reatribuir registros orfaos restantes
    ChatMessage.objects.filter(contact=secondary).update(contact=primary)
    Cart.objects.filter(contact=secondary).update(contact=primary)
    Sale.objects.filter(contact=secondary).update(contact=primary)
    WppMessage.objects.filter(contact=secondary).update(contact=primary)

    sec_id = secondary.id
    secondary.delete()
    log_system_event('INFO', 'livechat.webhook.merge_contacts',
        f'Merged contact #{sec_id} into #{primary.id}')


def _handle_messages_update(payload):
    try:
        data = payload.get('data', {})
        updates = data if isinstance(data, list) else [data]

        status_map = {2: 'sent', 3: 'delivered', 4: 'read', 5: 'read'}
        string_status_map = {
            'SERVER_ACK': 'sent', 'DELIVERY_ACK': 'delivered',
            'READ': 'read', 'PLAYED': 'read',
        }
        STATUS_ORDER = {'pending': 0, 'sent': 1, 'delivered': 2, 'read': 3}

        for update in updates:
            # Formato real: flat com keyId/status (não nested key/update)
            wpp_message_id = (
                update.get('keyId') or
                update.get('key', {}).get('id')
            )
            if not wpp_message_id:
                continue

            raw_status = (
                update.get('status') or
                update.get('update', {}).get('status')
            )

            if isinstance(raw_status, int):
                new_status = status_map.get(raw_status)
            elif isinstance(raw_status, str):
                new_status = string_status_map.get(raw_status)
            else:
                continue

            if not new_status:
                continue

            lower_statuses = [s for s, o in STATUS_ORDER.items() if o < STATUS_ORDER[new_status]]
            now = datetime.now(tz=timezone.utc)

            ChatMessage.objects.filter(
                wpp_message_id=wpp_message_id,
                status__in=lower_statuses,
            ).update(status=new_status, status_updated_at=now)

    except Exception as e:
        log_system_event('ERROR', 'livechat.webhook.messages_update',
            f'{type(e).__name__}: {e}')
