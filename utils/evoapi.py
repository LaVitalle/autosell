from django.conf import settings
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import MediaMessage, TextMessage

# Configurações da Evolution API
EVOLUTION_TOKEN = settings.EVOLUTION_TOKEN
EVOLUTION_URL = settings.EVOLUTION_URL
EVOLUTION_INSTANCE_ID = settings.EVOLUTION_INSTANCE_ID
EVOLUTION_INSTANCE_TOKEN = settings.EVOLUTION_INSTANCE_TOKEN

# Cliente global (inicializado apenas quando necessário)
_evolution_client = None
_evolution_state = None

def get_client():
    """Obtém o cliente Evolution API, inicializando se necessário"""
    global _evolution_client, _evolution_state
    if _evolution_client is None:
        _evolution_client = EvolutionClient(EVOLUTION_URL, EVOLUTION_TOKEN)
        try:
            _evolution_state = _evolution_client.instance_operations.connect(EVOLUTION_INSTANCE_ID, EVOLUTION_INSTANCE_TOKEN)
        except Exception as e:
            print(f"Aviso: Não foi possível conectar à instância: {e}")
            _evolution_state = None
    return _evolution_client


def send_text_message(message: TextMessage):
    """Envia uma mensagem de texto via Evolution API"""
    try:
        _evolution_client = get_client()
        return _evolution_client.messages.send_text(EVOLUTION_INSTANCE_ID, message, EVOLUTION_INSTANCE_TOKEN)      
    except Exception as e:
        print(f"Erro ao enviar mensagem de texto: {e}")
        return None

def send_media_message(message: MediaMessage):
    """Envia uma mensagem de mídia via Evolution API"""
    try:
        _evolution_client = get_client()
        return _evolution_client.messages.send_media(EVOLUTION_INSTANCE_ID, message, EVOLUTION_INSTANCE_TOKEN)
    except Exception as e:
        print(f"Erro ao enviar mensagem de mídia: {e}")
        return None