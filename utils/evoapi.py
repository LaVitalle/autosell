from django.conf import settings
from requests import post

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
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem de texto: {e}")
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
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem de mídia: {e}")
        return None