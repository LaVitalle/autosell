import os
from django.conf import settings
from supabase import create_client, Client

# Inicializa o cliente Supabase usando a SERVICE_ROLE_KEY (segura, backend)
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

BUCKET_NAME = "Images"  # ajuste para o nome exato do seu bucket


def upload_file_to_supabase(file_name: str, file) -> str:
    """
    Faz upload de um arquivo para o Supabase Storage e retorna a URL pública.

    :param file_name: Nome final do arquivo no bucket (ex: 'products/123.png')
    :param file: Arquivo do Django (InMemoryUploadedFile ou UploadedFile)
    :return: URL pública do arquivo
    """
    # Lê os bytes do arquivo
    file_content = file.read() if hasattr(file, "read") else file

    file_name = clean_file_name(file_name)

    # Faz upload
    try:
        result = supabase.storage.from_(BUCKET_NAME).upload(file_name, file_content)
    except Exception as e:
        raise Exception(f"Erro no upload para Supabase: {e}")

    # Gera a URL pública
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

    if not public_url:
        raise Exception("Não foi possível gerar a URL pública do arquivo")

    return public_url

def delete_file_from_supabase(file_url: str) -> bool:
    """
    Deleta um arquivo do Supabase Storage.

    :param file_name: Nome do arquivo no bucket (ex: 'products/123.png')
    :return: True se deletado com sucesso, False caso contrário
    """
    try:
        file_name = file_url.split(f"/{BUCKET_NAME}/")[-1]
        file_name = file_name.split("?")[0]
        result = supabase.storage.from_(BUCKET_NAME).remove([file_name])
        if result and result[0].get("error"):
            print(f"Erro ao deletar arquivo: {result['error']}")
            return False
        return True
    except Exception as e:
        print(f"Exceção ao deletar arquivo: {e}")
        return False

#Função para limpar o nome do arquivo de caracteres especiais e caracteres com acentuação, não remove caracteres de url
def clean_file_name(file_name: str) -> str:
    return file_name.replace(" ", "").replace("-", "").replace(":", "").replace("(", "").replace(")", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c").replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U").replace("Ç","C")