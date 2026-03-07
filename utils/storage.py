import os
from django.conf import settings


def clean_file_name(file_name: str) -> str:
    return file_name.replace(" ", "").replace("-", "").replace(":", "").replace("(", "").replace(")", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c").replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U").replace("Ç","C")


def upload_file(file_name: str, file) -> str:
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
