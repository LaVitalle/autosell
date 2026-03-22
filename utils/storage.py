import os
import re
import uuid
import base64
import unicodedata
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp3', '.ogg', '.opus', '.m4a', '.aac'}


def clean_file_name(file_name: str) -> str:
    nfkd = unicodedata.normalize('NFKD', file_name)
    ascii_name = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^\w.]', '', ascii_name)


def upload_file(file_name: str, file) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    file_name = clean_file_name(file_name)

    file_content = file.read() if hasattr(file, "read") else file
    saved_name = default_storage.save(file_name, ContentFile(file_content))

    return default_storage.url(saved_name)


def upload_media_from_base64(file_name: str, base64_data: str) -> str:
    """Upload de mídia a partir de dados base64. Retorna URL do MinIO ou None."""
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    file_name = clean_file_name(file_name)
    file_content = base64.b64decode(base64_data)
    saved_name = default_storage.save(file_name, ContentFile(file_content))
    return default_storage.url(saved_name)


def upload_media_from_url(file_name: str, url: str) -> str:
    """Download de mídia a partir de URL e upload para MinIO. Retorna URL ou None."""
    import requests
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    file_name = clean_file_name(file_name)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    saved_name = default_storage.save(file_name, ContentFile(response.content))
    return default_storage.url(saved_name)


def delete_file(file_url: str) -> bool:
    if not file_url:
        return False
    try:
        # Extrair o nome do arquivo da URL completa do MinIO
        # URL format: https://minio-host/bucket/path/to/file.jpg
        # Ou formato antigo: /media/path/to/file.jpg
        if file_url.startswith(settings.MEDIA_URL):
            relative_path = file_url.replace(settings.MEDIA_URL, '', 1)
        elif '/media/' in file_url:
            relative_path = file_url.split('/media/', 1)[1]
        else:
            # Tentar extrair após o bucket name
            bucket = settings.MINIO_BUCKET_NAME
            if f'/{bucket}/' in file_url:
                relative_path = file_url.split(f'/{bucket}/', 1)[1]
            else:
                relative_path = file_url

        if default_storage.exists(relative_path):
            default_storage.delete(relative_path)
        return True
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
        return False
