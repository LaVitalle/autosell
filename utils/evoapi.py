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


def get_base64_from_media_message(webhook_data: dict, convert_to_mp4: bool = False):
    """Obtém base64 de uma mensagem de mídia via Evolution API.
    Recebe o objeto 'data' completo do webhook (com key + message)."""
    try:
        # A API espera { "message": { "key": {...}, "message": {...} } }
        msg_payload = {
            "key": webhook_data.get("key", {}),
            "message": webhook_data.get("message", {}),
        }
        response = post(
            f"{EVOLUTION_URL}/chat/getBase64FromMediaMessage/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "message": msg_payload,
                "convertToMp4": convert_to_mp4
            },
            timeout=30
        )
        if response.status_code >= 400:
            log_system_event('ERROR', 'utils.evoapi.get_base64_from_media',
                f'API retornou status {response.status_code}: {response.text[:500]}')
            return None
        data = response.json()
        return data.get('base64', None)
    except Exception as e:
        log_system_event('ERROR', 'utils.evoapi.get_base64_from_media',
            f'Erro ao obter base64: {e}')
        return None


def resolve_contact_number(contact):
    """Retorna o identificador para envio: prioriza phone (JID), fallback lid (LID)."""
    return contact.phone or contact.lid or ''


def resolve_conversation_number(conversation):
    """Retorna o numero para envio a partir de uma conversa.
    Prioriza phone do contato (JID), fallback para remote_jid (LID)."""
    if conversation.contact.phone:
        return conversation.contact.phone
    return conversation.remote_jid


def build_product_text(product):
    parts = [f'*{product.name}*']
    if product.description:
        parts.append(f'_{product.description}_')
    parts.append('')
    if product.stock_active:
        parts.append(f'*Restam:* {product.stock_quantity} unidades')
    parts.append(f'*Preco:* R$ {product.price}')
    return '\n'.join(parts)


def build_catalog_text(products_by_category, uncategorized_products):
    """Monta texto do catalogo completo organizado por categoria."""
    parts = ['\U0001f4cb *Cardapio do Dia*']

    for category_name, products in products_by_category:
        parts.append('')
        parts.append(f'*\U0001f3f7 {category_name}*')
        parts.append('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')
        for p in products:
            line = f'\u2022 *{p.name}* \u2014 R$ {p.price}'
            parts.append(line)
            if p.description:
                parts.append(f'  _{p.description}_')
            if p.stock_active and p.stock_quantity > 0:
                parts.append(f'  Restam: {p.stock_quantity} unidades')

    if uncategorized_products:
        parts.append('')
        parts.append('*Outros*')
        parts.append('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')
        for p in uncategorized_products:
            line = f'\u2022 *{p.name}* \u2014 R$ {p.price}'
            parts.append(line)
            if p.description:
                parts.append(f'  _{p.description}_')
            if p.stock_active and p.stock_quantity > 0:
                parts.append(f'  Restam: {p.stock_quantity} unidades')

    return '\n'.join(parts)


def send_product_message(phone, product):
    text = build_product_text(product)
    if product.image_url:
        return send_media_message(
            number=phone,
            mediatype='image',
            mimetype='image/png',
            caption=text,
            media=product.image_url if product.image_url.startswith('http') else f'{settings.SITE_URL}{product.image_url}',
            fileName=f'{product.name}.png'
        )
    return send_text_message(phone, text)


def mark_message_as_read(remote_jid, message_ids):
    try:
        response = post(
            f"{EVOLUTION_URL}/chat/markMessageAsRead/{EVOLUTION_INSTANCE_ID}",
            headers={
                "Content-Type": "application/json",
                "apikey": f"{EVOLUTION_INSTANCE_TOKEN}"
            },
            json={
                "readMessages": [
                    {"remoteJid": remote_jid, "fromMe": False, "id": mid}
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