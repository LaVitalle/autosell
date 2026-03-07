import os
import re
import unicodedata
from django.conf import settings

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def clean_file_name(file_name: str) -> str:
    nfkd = unicodedata.normalize('NFKD', file_name)
    ascii_name = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^\w.]', '', ascii_name)


def upload_file(file_name: str, file) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    file_name = clean_file_name(file_name)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_content = file.read() if hasattr(file, "read") else file
    with open(file_path, 'wb') as f:
        f.write(file_content)

    return f'{settings.MEDIA_URL}{file_name}'


def delete_file(file_url: str) -> bool:
    if not file_url:
        return False
    try:
        relative_path = file_url.replace(settings.MEDIA_URL, '', 1)
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
        return False
