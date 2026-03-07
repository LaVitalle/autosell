# AutoSell - Documentacao Completa do Sistema

## 1. Visao Geral

**AutoSell** e um sistema web de gestao de vendas e marketing via WhatsApp, construido com Django 5.2.5. O sistema permite cadastrar produtos e categorias, gerenciar contatos e enviar mensagens automatizadas (texto e midia) via WhatsApp atraves da **Evolution API**. As imagens sao armazenadas no **Supabase Storage**.

- **Dominio de producao:** `autosell.upperlavtech.com`
- **Linguagem:** Python 3.13
- **Framework:** Django 5.2.5
- **Frontend:** Templates Django + Tailwind CSS (via CDN)
- **Banco de dados:** SQLite (dev) / PostgreSQL (prod)
- **Armazenamento de imagens:** Supabase Storage
- **Mensageria WhatsApp:** Evolution API
- **Autenticacao:** Sistema nativo do Django (session-based)

---

## 2. Arquitetura e Estrutura de Diretorios

```
autosell/
├── autosell/                  # Projeto Django principal (settings, urls, wsgi/asgi)
│   ├── __init__.py
│   ├── settings.py            # Configuracoes do projeto
│   ├── urls.py                # Roteamento principal
│   ├── wsgi.py                # Entry point WSGI
│   └── asgi.py                # Entry point ASGI
│
├── dashboard/                 # App - Dashboard (pagina inicial)
│   ├── views.py               # View unica: renderiza dashboard.html
│   ├── models.py              # Vazio (sem models proprios)
│   └── admin.py
│
├── products/                  # App - Gestao de Produtos
│   ├── models.py              # Model Product
│   ├── views.py               # CRUD completo de produtos
│   ├── forms.py               # ProductForm com validacoes
│   ├── urls.py                # Rotas /products/
│   ├── admin.py               # Registro no Django Admin
│   ├── templates/
│   │   └── confirm_delete.html
│   └── migrations/
│
├── categories/                # App - Gestao de Categorias
│   ├── models.py              # Model Category (M2M com Product)
│   ├── views.py               # CRUD completo de categorias
│   ├── forms.py               # CategoryForm com selecao de produtos
│   ├── urls.py                # Rotas /categories/
│   ├── admin.py               # Registro no Django Admin
│   └── migrations/
│
├── contacts/                  # App - Gestao de Contatos
│   ├── models.py              # Model Contact
│   ├── views.py               # CRUD completo de contatos
│   ├── forms.py               # ContactForm com validacao de telefone
│   ├── urls.py                # Rotas /contacts/
│   └── migrations/
│
├── wppmessages/               # App - Envio de Mensagens WhatsApp
│   ├── models.py              # Model Message (FK para Contact, Product, Category)
│   ├── views.py               # Gerenciador de mensagens + webhook
│   ├── forms.py               # MessageForm com tipo dinamico
│   ├── urls.py                # Rotas /messages/
│   └── migrations/
│
├── utils/                     # Utilitarios
│   ├── evoapi.py              # Integracao com Evolution API (WhatsApp)
│   └── supabase_storage.py    # Upload/delete de arquivos no Supabase Storage
│
├── templates/                 # Templates globais
│   └── registration/
│       └── login.html         # Pagina de login customizada
│
├── .env                       # Variaveis de ambiente (nao versionado)
├── .gitignore
├── requirements.txt           # Dependencias Python
└── tailwind.config.js         # Configuracao do Tailwind CSS
```

---

## 3. Models (Banco de Dados)

### 3.1 Product (`products/models.py`)

| Campo            | Tipo                    | Restricoes                    |
|------------------|-------------------------|-------------------------------|
| `name`           | CharField(90)           | Obrigatorio                   |
| `description`    | TextField(255)          | Opcional (null=True)          |
| `price`          | DecimalField(10,2)      | Obrigatorio                   |
| `image_url`      | URLField(500)           | Opcional (null=True)          |
| `stock_active`   | BooleanField            | Default: False                |
| `stock_quantity` | IntegerField            | Default: 0                    |
| `updated_at`     | DateTimeField           | auto_now                      |
| `created_at`     | DateTimeField           | auto_now_add                  |

### 3.2 Category (`categories/models.py`)

| Campo        | Tipo                          | Restricoes              |
|--------------|-------------------------------|-------------------------|
| `name`       | CharField(90)                 | Obrigatorio             |
| `description`| TextField(255)                | Opcional (null=True)    |
| `image_url`  | URLField(500)                 | Opcional (null=True)    |
| `products`   | ManyToManyField(Product)      | related_name='categories' |
| `updated_at` | DateTimeField                 | auto_now                |
| `created_at` | DateTimeField                 | auto_now_add            |

**Relacionamento:** Uma categoria contem N produtos (ManyToMany). Um produto pode pertencer a varias categorias.

### 3.3 Contact (`contacts/models.py`)

| Campo        | Tipo            | Restricoes       |
|--------------|-----------------|------------------|
| `name`       | CharField(60)   | Obrigatorio      |
| `phone`      | CharField(20)   | Obrigatorio      |
| `updated_at` | DateTimeField   | auto_now         |
| `created_at` | DateTimeField   | auto_now_add     |

**Validacao de telefone:** O formulario normaliza o numero para formato `55XXXXXXXXXXX` (13 digitos, com DDI do Brasil).

### 3.4 Message (`wppmessages/models.py`)

| Campo      | Tipo                       | Restricoes                             |
|------------|----------------------------|----------------------------------------|
| `contact`  | ForeignKey(Contact)        | Obrigatorio, CASCADE                   |
| `type`     | CharField(20)              | Choices: `product`, `category`         |
| `product`  | ForeignKey(Product)        | Opcional, CASCADE                      |
| `category` | ForeignKey(Category)       | Opcional, CASCADE                      |
| `sent_at`  | DateTimeField              | auto_now_add                           |
| `status`   | CharField(20)              | Choices: `pending`, `sent`, `failed`   |

**Ordenacao padrao:** `-sent_at` (mais recentes primeiro)

---

## 4. Diagrama de Relacionamentos

```
┌──────────┐     M:N      ┌───────────┐
│ Product  │◄────────────►│ Category  │
└────┬─────┘              └─────┬─────┘
     │ FK (opcional)            │ FK (opcional)
     │                          │
     └──────────┐  ┌────────────┘
                │  │
           ┌────▼──▼────┐
           │  Message    │
           └────┬────────┘
                │ FK (obrigatorio)
                ▼
           ┌──────────┐
           │ Contact   │
           └──────────┘
```

---

## 5. Rotas (URLs)

### 5.1 Rotas Principais (`autosell/urls.py`)

| Rota                          | View/Include                        | Nome                    |
|-------------------------------|-------------------------------------|-------------------------|
| `/`                           | `dashboard.views.dashboard`         | `dashboard`             |
| `/admin/`                     | Django Admin                        | -                       |
| `/products/`                  | `include('products.urls')`          | -                       |
| `/categories/`                | `include('categories.urls')`        | -                       |
| `/contacts/`                  | `include('contacts.urls')`          | -                       |
| `/messages/`                  | `include('wppmessages.urls')`       | -                       |
| `/accounts/login/`            | Django LoginView                    | `login`                 |
| `/accounts/logout/`           | Django LogoutView                   | `logout`                |
| `/accounts/password_change/`  | Django PasswordChangeView           | `password_change`       |

### 5.2 Rotas de Produtos (`products/urls.py`)

| Rota                          | View                   | Nome               | Metodo    |
|-------------------------------|------------------------|---------------------|-----------|
| `/products/`                  | `get_all_products`     | `get_all_products`  | GET       |
| `/products/<id>`              | `get_by_id`            | `get_by_id`         | GET       |
| `/products/create`            | `create_product`       | `create_product`    | GET/POST  |
| `/products/delete/<id>`       | `delete_product`       | `delete_by_id`      | GET/POST  |
| `/products/edit/<id>`         | `edit_product`         | `edit_product`      | GET/POST  |

### 5.3 Rotas de Categorias (`categories/urls.py`)

| Rota                            | View                   | Nome                   | Metodo    |
|---------------------------------|------------------------|------------------------|-----------|
| `/categories/`                  | `get_all_categories`   | `get_all_categories`   | GET       |
| `/categories/<id>`              | `get_category_by_id`   | `get_category_by_id`   | GET       |
| `/categories/create`            | `create_category`      | `create_category`      | GET/POST  |
| `/categories/edit/<id>`         | `edit_category`        | `edit_category`        | GET/POST  |
| `/categories/delete/<id>`       | `delete_category`      | `delete_category`      | GET/POST  |

### 5.4 Rotas de Contatos (`contacts/urls.py`)

| Rota                          | View                | Nome                | Metodo    |
|-------------------------------|---------------------|---------------------|-----------|
| `/contacts/`                  | `get_all_contacts`  | `get_all_contacts`  | GET       |
| `/contacts/create`            | `create_contact`    | `create_contact`    | GET/POST  |
| `/contacts/edit/<id>`         | `edit_contact`      | `edit_contact`      | GET/POST  |
| `/contacts/delete/<id>`       | `delete_contact`    | `delete_contact`    | GET/POST  |

### 5.5 Rotas de Mensagens (`wppmessages/urls.py`)

| Rota                | View                | Nome                 | Metodo    |
|---------------------|---------------------|----------------------|-----------|
| `/messages/`        | `messages_manager`  | `messages_manager`   | GET/POST  |
| `/messages/hook`    | `hook`              | `hook`               | POST      |

---

## 6. Integracoes Externas

### 6.1 Evolution API (WhatsApp) - `utils/evoapi.py`

Responsavel por enviar mensagens via WhatsApp usando a Evolution API.

**Configuracoes necessarias (.env):**
- `EVOLUTION_TOKEN` - Token global da API
- `EVOLUTION_URL` - URL base da Evolution API
- `EVOLUTION_INSTANCE_ID` - ID da instancia WhatsApp
- `EVOLUTION_INSTANCE_TOKEN` - Token da instancia

**Funcoes disponiveis:**

| Funcao                | Descricao                                      | Endpoint                              |
|-----------------------|------------------------------------------------|---------------------------------------|
| `send_text_message`   | Envia mensagem de texto simples                | `POST /message/sendText/<instance>`   |
| `send_media_message`  | Envia mensagem com midia (imagem, etc)         | `POST /message/sendMedia/<instance>`  |

**Formato da mensagem de produto enviada:**
```
*Nome do Produto*
_Descricao do produto_

*Restam:* X unidades  (se stock_active=True)
*Preco:* R$ XX.XX
```

### 6.2 Supabase Storage - `utils/supabase_storage.py`

Gerencia upload e exclusao de imagens no Supabase Storage.

**Configuracoes necessarias (.env):**
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_SERVICE_ROLE_KEY` - Service Role Key (backend)

**Bucket:** `Images`

**Funcoes disponiveis:**

| Funcao                      | Descricao                                              |
|-----------------------------|--------------------------------------------------------|
| `upload_file_to_supabase`   | Faz upload e retorna a URL publica                     |
| `delete_file_from_supabase` | Deleta arquivo do bucket pelo URL                      |
| `clean_file_name`           | Remove caracteres especiais/acentos do nome do arquivo |

**Convencao de nomes de arquivo:**
- Produtos: `products/<uuid><nome_original>`
- Categorias: `categories/<uuid><nome_original>`

---

## 7. Fluxos Principais

### 7.1 Envio de Mensagem de Produto Individual

```
1. Usuario acessa /messages/ e seleciona:
   - Tipo: "product"
   - Contato: seleciona da lista
   - Produto: seleciona da lista
2. Sistema cria registro Message com status "pending"
3. Verifica se o produto tem image_url:
   - SIM: chama send_media_message() com imagem + caption formatado
   - NAO: chama send_text_message() com texto formatado
4. Se sucesso: status -> "sent"
   Se falha: status -> "failed"
```

### 7.2 Envio de Mensagem de Categoria (multiplos produtos)

```
1. Usuario seleciona tipo "category" + contato + categoria
2. Sistema cria registro Message com status "pending"
3. Itera sobre TODOS os produtos da categoria:
   - Para cada produto, envia mensagem individual (midia ou texto)
   - Erros individuais sao ignorados (continue)
4. Se todos enviados: status -> "sent"
   Se erro geral: status -> "failed"
```

### 7.3 Webhook (`/messages/hook`)

```
1. Recebe requisicao POST externa (ex: Evolution API callback)
2. Decodifica o body da requisicao
3. Encaminha o conteudo como mensagem de texto WhatsApp
   para o numero fixo: 5545998231771
```

**Nota:** Este endpoint e `@csrf_exempt` - nao exige token CSRF.

### 7.4 CRUD de Produtos/Categorias com Upload de Imagem

```
Criar:
1. Usuario preenche formulario + seleciona imagem (opcional)
2. Se imagem fornecida:
   - Gera nome unico: <tipo>/<uuid><nome_original>
   - Upload para Supabase Storage
   - Salva URL publica no campo image_url
3. Salva registro no banco

Editar:
1. Carrega dados existentes no formulario
2. Se nova imagem fornecida:
   - Upload da nova imagem
   - Deleta imagem anterior do Supabase
   - Atualiza image_url
3. Salva alteracoes

Deletar:
1. Exibe pagina de confirmacao
2. Se confirmado (POST com _method=DELETE):
   - Deleta imagem do Supabase (se existir)
   - Remove registro do banco
```

---

## 8. Seguranca

### 8.1 Autenticacao
- Todas as views (exceto `hook`) exigem `@login_required`
- Login via sistema nativo do Django (`/accounts/login/`)
- Sessao com cookies seguros em producao

### 8.2 CORS e CSRF
- CORS configurado para origens especificas (autosell.upperlavtech.com, localhost, evo.upperlavtech.com)
- CSRF habilitado em todos os formularios (exceto webhook)
- `CSRF_COOKIE_SECURE` e `SESSION_COOKIE_SECURE` ativos em producao

### 8.3 SSL/HTTPS
- `SECURE_PROXY_SSL_HEADER` configurado para proxy reverso
- `SECURE_SSL_REDIRECT` ativo em producao

### 8.4 Variaveis de Ambiente
- Secrets gerenciados via `python-decouple` (arquivo `.env`)
- `.env` no `.gitignore`

---

## 9. Configuracao de Ambiente

### 9.1 Variaveis de Ambiente Necessarias (.env)

```
SECRET_KEY=<django-secret-key>
PROD=True|False

# Banco de Dados (apenas producao)
DB_NAME=<nome>
DB_USER=<usuario>
DB_PASSWORD=<senha>
DB_HOST=<host>
DB_PORT=<porta>

# Supabase
SUPABASE_URL=<url-do-projeto>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# Evolution API
EVOLUTION_TOKEN=<token-global>
EVOLUTION_URL=<url-base>
EVOLUTION_INSTANCE_ID=<id-instancia>
EVOLUTION_INSTANCE_TOKEN=<token-instancia>
```

### 9.2 Banco de Dados
- **Desenvolvimento:** SQLite (automatico, sem configuracao)
- **Producao:** PostgreSQL (via `psycopg2-binary`)

---

## 10. Dependencias Principais

| Pacote                    | Versao  | Uso                                |
|---------------------------|---------|------------------------------------|
| Django                    | 5.2.5   | Framework web                      |
| django-cors-headers       | 4.3.1   | Configuracao de CORS               |
| supabase                  | 2.18.1  | SDK Supabase (storage)             |
| psycopg2-binary           | 2.9.10  | Driver PostgreSQL                  |
| python-decouple           | 3.8     | Gestao de variaveis de ambiente    |
| requests                  | 2.32.5  | Chamadas HTTP (Evolution API)      |
| httpx                     | 0.28.1  | Cliente HTTP async (usado por supabase) |
| pydantic                  | 2.11.7  | Validacao de dados (usado por supabase) |

---

## 11. Django Admin

Models registrados no admin com configuracoes customizadas:

### ProductAdmin
- **Colunas:** name, price, stock_active, stock_quantity, updated_at, created_at
- **Busca:** name, description
- **Filtros:** stock_active, updated_at, created_at
- **Ordenacao:** -updated_at, -created_at
- **Paginacao:** 12 itens por pagina

### CategoryAdmin
- **Colunas:** name, description, image_url, updated_at, created_at
- **Busca:** name, description
- **Filtros:** updated_at, created_at
- **Ordenacao:** -updated_at, -created_at
- **Paginacao:** 12 itens por pagina

---

## 12. Frontend

- **CSS Framework:** Tailwind CSS via CDN (`cdn.tailwindcss.com`)
- **Design System:** Paleta neutra (neutral-50 a neutral-950), com suporte a dark mode
- **Dark Mode:** Baseado em classe (`darkMode: 'class'`), persistido no `localStorage`
- **Templates:** Django template engine com heranca (extends `dashboard.html`)
- **Formularios:** Estilizados com classes Tailwind inline nos widgets dos forms

---

## 13. Observacoes e Pontos de Atencao

### Bug na configuracao DEBUG
```python
DEBUG = True if PROD == 'False' else True  # Sempre True!
```
A logica condicional resulta em `DEBUG = True` independente do valor de `PROD`. O correto seria:
```python
DEBUG = PROD != 'True'
```

### Webhook sem autenticacao
O endpoint `/messages/hook` e `@csrf_exempt` e nao possui autenticacao, e envia o body recebido diretamente para um numero fixo. Isso pode ser explorado para spam.

### Codigo comentado
O arquivo `categories/urls.py` contem codigo comentado de rotas de produtos (linhas 12-16) que deveria ser removido.

### Tratamento de erros no envio de categoria
Quando o envio de mensagem por categoria falha para um produto individual, o erro e silenciosamente ignorado (`continue`), e o status final e marcado como "sent" mesmo que alguns produtos nao tenham sido enviados.

### Ausencia de paginacao nas listagens
As views `get_all_products`, `get_all_categories` e `get_all_contacts` retornam todos os registros sem paginacao, o que pode causar problemas de performance com muitos registros.

### Ausencia de testes
Os arquivos `tests.py` em todos os apps estao vazios. Nao ha testes automatizados implementados.
