from django.conf import settings
from requests import post
from utils.api_response import log_system_event

# Configurações da Evolution API
EVOLUTION_TOKEN = settings.EVOLUTION_TOKEN
EVOLUTION_URL = settings.EVOLUTION_URL
EVOLUTION_INSTANCE_ID = settings.EVOLUTION_INSTANCE_ID
EVOLUTION_INSTANCE_TOKEN = settings.EVOLUTION_INSTANCE_TOKEN


def send_text_message(number: str, text: str):
    """Envia uma mensagem de texto via Evolution API"""
    try:
        response = post(
            f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "number": number,
                "text": text
            }
        )
        log_system_event('INFO', 'utils.evoapi.send_text_message',
            f'Enviando para {number} | Status: {response.status_code} | Response: {response.text[:500]}')
        if response.status_code >= 400:
            log_system_event('ERROR', 'utils.evoapi.send_text_message',
                f'API retornou status {response.status_code}: {response.text}')
            return None
        return response.json()
    except Exception as e:
        log_system_event('ERROR', 'utils.evoapi.send_text_message', f'Erro ao enviar mensagem de texto: {e}')
        return None

def send_media_message(number: str, mediatype: str, mimetype: str, caption: str, media: str, fileName: str):
    """Envia uma mensagem de mídia via Evolution API"""
    try:
        response = post(
            f"{EVOLUTION_URL}/message/sendMedia/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "number": number,
                "mediatype": mediatype,
                "mimetype": mimetype,
                "caption": caption,
                "media": media,
                "fileName": fileName
            }
        )
        if response.status_code >= 400:
            log_system_event('ERROR', 'utils.evoapi.send_media_message',
                f'API retornou status {response.status_code}: {response.text}')
            return None
        return response.json()
    except Exception as e:
        log_system_event('ERROR', 'utils.evoapi.send_media_message', f'Erro ao enviar mensagem de midia: {e}')
        return None


def build_product_text(product):
    parts = [f'*{product.name}*']
    if product.description:
        parts.append(f'_{product.description}_')
    parts.append('')
    if product.stock_active:
        parts.append(f'*Restam:* {product.stock_quantity} unidades')
    parts.append(f'*Preco:* R$ {product.price}')
    return '\n'.join(parts)


def send_product_message(phone, product):
    text = build_product_text(product)
    if product.image_url:
        return send_media_message(
            number=phone,
            mediatype='image',
            mimetype='image/png',
            caption=text,
            media=f'{settings.SITE_URL}{product.image_url}',
            fileName=f'{product.name}.png'
        )
    return send_text_message(phone, text)


def mark_message_as_read(remote_jid, message_ids):
    try:
        response = post(
            f"{EVOLUTION_URL}/chat/readMessage/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "readMessages": [
                    {"remoteJid": remote_jid, "id": mid}
                    for mid in message_ids
                ]
            }
        )
        if response.status_code >= 400:
            log_system_event('ERROR', 'utils.evoapi.mark_message_as_read',
                f'API retornou status {response.status_code}: {response.text}')
            return None
        return response.json()
    except Exception as e:
        log_system_event('ERROR', 'utils.evoapi.mark_message_as_read', f'Erro ao marcar como lida: {e}')
        return None


def send_presence(number, presence='composing'):
    try:
        response = post(
            f"{EVOLUTION_URL}/chat/sendPresence/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "number": number,
                "presence": presence
            }
        )
        if response.status_code >= 400:
            log_system_event('ERROR', 'utils.evoapi.send_presence',
                f'API retornou status {response.status_code}: {response.text}')
            return None
        return response.json()
    except Exception as e:
        log_system_event('ERROR', 'utils.evoapi.send_presence', f'Erro ao enviar presenca: {e}')
        return None