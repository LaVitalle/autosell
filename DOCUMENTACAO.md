# AutoSell - Documentacao Completa do Sistema

## 1. Visao Geral

**AutoSell** e um sistema web de gestao de vendas e marketing via WhatsApp, construido com Django 5.2.5. O sistema permite cadastrar produtos e categorias, gerenciar contatos e enviar mensagens automatizadas (texto e midia) via WhatsApp atraves da **Evolution API**. As imagens sao armazenadas localmente no servidor via **Django MEDIA_ROOT**.

- **Dominio de producao:** `autosell.upperlavtech.com`
- **Linguagem:** Python 3.13
- **Framework:** Django 5.2.5
- **Frontend:** Templates Django + Tailwind CSS (via CDN)
- **Banco de dados:** SQLite (dev) / PostgreSQL (prod)
- **Armazenamento de imagens:** Django Local (MEDIA_ROOT)
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
│   ├── views.py               # CRUD completo de produtos (templates)
│   ├── api_views.py           # Endpoints API (JSON) com stats
│   ├── forms.py               # ProductForm com validacoes
│   ├── urls.py                # Rotas /products/ (com trailing slashes)
│   ├── admin.py               # Registro no Django Admin
│   ├── templates/
│   │   ├── products.html      # Listagem (render via JS/API)
│   │   ├── product.html       # Detalhe do produto
│   │   ├── product_form.html  # Formulario unificado (criar/editar)
│   │   └── confirm_delete.html
│   └── migrations/
│
├── categories/                # App - Gestao de Categorias
│   ├── models.py              # Model Category (M2M com Product)
│   ├── views.py               # CRUD completo de categorias (templates)
│   ├── api_views.py           # Endpoints API (JSON)
│   ├── forms.py               # CategoryForm com selecao de produtos
│   ├── urls.py                # Rotas /categories/
│   ├── admin.py               # Registro no Django Admin
│   └── migrations/
│
├── contacts/                  # App - Gestao de Contatos
│   ├── models.py              # Model Contact
│   ├── views.py               # CRUD completo de contatos (templates)
│   ├── api_views.py           # Endpoints API (JSON)
│   ├── forms.py               # ContactForm com validacao de telefone
│   ├── urls.py                # Rotas /contacts/
│   └── migrations/
│
├── wppmessages/               # App - Envio de Mensagens WhatsApp
│   ├── models.py              # Model Message (FK para Contact, Product, Category)
│   ├── views.py               # Gerenciador de mensagens + webhook
│   ├── api_views.py           # Endpoint API de envio de mensagem
│   ├── forms.py               # MessageForm com tipo dinamico
│   ├── urls.py                # Rotas /messages/
│   └── migrations/
│
├── systemlogs/                # App - Logs do sistema
│   ├── models.py              # Model para logs
│   └── migrations/
│
├── utils/                     # Utilitarios
│   ├── evoapi.py              # Integracao com Evolution API (WhatsApp)
│   ├── storage.py             # Upload/delete de arquivos locais (MEDIA_ROOT)
│   └── api_response.py        # Helpers para respostas padronizadas de API
│
├── templates/                 # Templates globais
│   └── registration/
│       └── login.html         # Pagina de login customizada
│
├── media/                     # Arquivos de midia (imagens) - nao versionado
│   ├── products/              # Imagens de produtos
│   └── categories/            # Imagens de categorias
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
| `image_url`      | CharField(500)          | Opcional (null=True, blank=True) |
| `stock_active`   | BooleanField            | Default: False. Indica producao limitada (controle de estoque ativo) |
| `stock_quantity` | IntegerField            | Default: 0. Quantidade disponivel quando stock_active=True |
| `updated_at`     | DateTimeField           | auto_now                      |
| `created_at`     | DateTimeField           | auto_now_add                  |

### 3.2 Category (`categories/models.py`)

| Campo        | Tipo                          | Restricoes              |
|--------------|-------------------------------|-------------------------|
| `name`       | CharField(90)                 | Obrigatorio             |
| `description`| TextField(255)                | Opcional (null=True)    |
| `image_url`  | CharField(500)                | Opcional (null=True, blank=True) |
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
| `/media/<path>`               | `django.views.static.serve`         | -                       |

### 5.2 Rotas de Produtos (`products/urls.py`)

| Rota                           | View                   | Nome               | Metodo    |
|--------------------------------|------------------------|---------------------|-----------|
| `/products/`                   | `get_all_products`     | `get_all_products`  | GET       |
| `/products/<id>/`              | `get_by_id`            | `get_by_id`         | GET       |
| `/products/create/`            | `create_product`       | `create_product`    | GET/POST  |
| `/products/delete/<id>/`       | `delete_product`       | `delete_by_id`      | GET/POST  |
| `/products/edit/<id>/`         | `edit_product`         | `edit_product`      | GET/POST  |
| `/products/api/`               | `api_list_products`    | `api_list_products` | GET       |
| `/products/api/create/`        | `api_create_product`   | `api_create_product`| POST      |
| `/products/api/<id>/edit/`     | `api_edit_product`     | `api_edit_product`  | POST      |
| `/products/api/<id>/delete/`   | `api_delete_product`   | `api_delete_product`| POST      |

**API de listagem (`api_list_products`):** Aceita parametros `page`, `per_page` (max 100) e `search`. Retorna campo `stats` com `total_products`, `total_value`, `with_stock_control` e `total_categories`.

### 5.3 Rotas de Categorias (`categories/urls.py`)

| Rota                            | View                   | Nome                   | Metodo    |
|---------------------------------|------------------------|------------------------|-----------|
| `/categories/`                  | `get_all_categories`   | `get_all_categories`   | GET       |
| `/categories/<id>`              | `get_category_by_id`   | `get_category_by_id`   | GET       |
| `/categories/create`            | `create_category`      | `create_category`      | GET/POST  |
| `/categories/edit/<id>`         | `edit_category`        | `edit_category`        | GET/POST  |
| `/categories/delete/<id>`       | `delete_category`      | `delete_category`      | GET/POST  |
| `/categories/api/`              | `api_list_categories`  | `api_list_categories`  | GET       |
| `/categories/api/create/`       | `api_create_category`  | `api_create_category`  | POST      |
| `/categories/api/<id>/edit/`    | `api_edit_category`    | `api_edit_category`    | POST      |
| `/categories/api/<id>/delete/`  | `api_delete_category`  | `api_delete_category`  | POST      |

### 5.4 Rotas de Contatos (`contacts/urls.py`)

| Rota                          | View                | Nome                | Metodo    |
|-------------------------------|---------------------|---------------------|-----------|
| `/contacts/`                  | `get_all_contacts`  | `get_all_contacts`  | GET       |
| `/contacts/create`            | `create_contact`    | `create_contact`    | GET/POST  |
| `/contacts/edit/<id>`         | `edit_contact`      | `edit_contact`      | GET/POST  |
| `/contacts/delete/<id>`       | `delete_contact`    | `delete_contact`    | GET/POST  |
| `/contacts/api/`              | `api_list_contacts` | `api_list_contacts` | GET       |
| `/contacts/api/create/`       | `api_create_contact`| `api_create_contact`| POST      |
| `/contacts/api/<id>/edit/`    | `api_edit_contact`  | `api_edit_contact`  | POST      |
| `/contacts/api/<id>/delete/`  | `api_delete_contact`| `api_delete_contact`| POST      |

### 5.5 Rotas de Mensagens (`wppmessages/urls.py`)

| Rota                | View                | Nome                 | Metodo    |
|---------------------|---------------------|----------------------|-----------|
| `/messages/`        | `messages_manager`  | `messages_manager`   | GET/POST  |
| `/messages/hook`    | `hook`              | `hook`               | POST      |
| `/messages/api/send/` | `api_send_message`| `api_send_message`   | POST      |

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

### 6.2 Armazenamento Local - `utils/storage.py`

Gerencia upload e exclusao de imagens no sistema de arquivos local (MEDIA_ROOT).

**Configuracoes necessarias (`settings.py`):**
- `MEDIA_URL = '/media/'` - Prefixo da URL para arquivos de midia
- `MEDIA_ROOT = BASE_DIR / 'media'` - Diretorio fisico no servidor
- `SITE_URL` - URL base do site (usado para construir URLs absolutas para APIs externas)

**Funcoes disponiveis:**

| Funcao           | Descricao                                              |
|------------------|--------------------------------------------------------|
| `upload_file`    | Valida extensao, salva arquivo em MEDIA_ROOT e retorna path relativo (`/media/...`). Retorna `None` se extensao invalida. |
| `delete_file`    | Deleta arquivo do disco pelo path relativo             |
| `clean_file_name`| Remove caracteres especiais/acentos via `unicodedata.normalize('NFKD')` |

**Extensoes permitidas:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**Convencao de nomes de arquivo:**
- Produtos: `media/products/<uuid><nome_original>`
- Categorias: `media/categories/<uuid><nome_original>`

**URLs de imagem:**
- No banco de dados e templates: path relativo (ex: `/media/products/abc.png`)
- Para APIs externas (Evolution API): URL absoluta construida com `SITE_URL` (ex: `https://autosell.upperlavtech.com/media/products/abc.png`)

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
3. Filtra produtos da categoria, EXCLUINDO esgotados:
   - Exclui produtos com stock_active=True e stock_quantity=0 (esgotados)
   - Produtos com stock_active=False (producao continua) sao sempre incluidos
4. Itera sobre os produtos filtrados:
   - Para cada produto, envia mensagem individual (midia ou texto)
   - Erros individuais sao contados
5. Se todos enviados: status -> "sent" (HTTP 200)
   Se envio parcial: status -> "sent" (HTTP 207)
   Se todos falharam: status -> "failed" (HTTP 500)
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

Produtos usam um template unificado (`product_form.html`) para criacao e edicao. O formulario de edicao exibe preview da imagem atual.

```
Criar:
1. Usuario preenche formulario + seleciona imagem (opcional)
2. Se imagem fornecida:
   - Valida extensao (jpg, jpeg, png, gif, webp)
   - Gera nome unico: <tipo>/<uuid><nome_original>
   - Salva arquivo em MEDIA_ROOT
   - Salva path relativo (/media/...) no campo image_url
3. Salva registro no banco

Editar:
1. Carrega dados existentes no formulario
2. Exibe preview da imagem atual (se existir)
3. Se nova imagem fornecida:
   - Valida extensao
   - Upload da nova imagem para MEDIA_ROOT
   - Deleta imagem anterior do disco
   - Atualiza image_url
4. Salva alteracoes

Deletar:
1. Exibe pagina de confirmacao
2. Se confirmado (POST com _method=DELETE):
   - Deleta imagem do disco (se existir)
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

### 8.3 XSS
- Listagem de produtos usa funcao `escapeHtml()` no JS para sanitizar dados dinamicos (`name`, `image_url`) antes de interpolar em template literals
- Templates Django usam auto-escaping nativo nos formularios

### 8.4 Validacao de Entrada
- Parametros de paginacao (`page`, `per_page`) sao validados como inteiros com fallback seguro
- `per_page` limitado a maximo de 100 para evitar abuso
- Upload de imagens restrito a extensoes permitidas (jpg, jpeg, png, gif, webp)
- Views de detalhe usam `get_object_or_404` para IDs inexistentes

### 8.5 SSL/HTTPS
- `SECURE_PROXY_SSL_HEADER` configurado para proxy reverso
- `SECURE_SSL_REDIRECT` ativo em producao

### 8.6 Variaveis de Ambiente
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

# URL do site (para URLs absolutas em APIs externas)
SITE_URL=https://autosell.upperlavtech.com

# Evolution API
EVOLUTION_TOKEN=<token-global>
EVOLUTION_URL=<url-base>
EVOLUTION_INSTANCE_ID=<id-instancia>
EVOLUTION_INSTANCE_TOKEN=<token-instancia>
EVOLUTION_SERVER_IP=<ip-do-servidor>
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
| psycopg2-binary           | 2.9.10  | Driver PostgreSQL                  |
| python-decouple           | 3.8     | Gestao de variaveis de ambiente    |
| requests                  | 2.32.5  | Chamadas HTTP (Evolution API)      |

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
- **Dark Mode:** Baseado em classe (`darkMode: 'class'`), persistido no `localStorage` (chave `theme`, valores `light`/`dark`). O tema e aplicado via script inline no `<head>` antes do body renderizar, evitando flash de modo claro (FOUC). Os toggles de tema usam classes Tailwind `dark:` para posicionamento instantaneo sem depender de JS.
- **Templates:** Django template engine com heranca (extends `dashboard.html`)
- **Formularios:** Estilizados com classes Tailwind inline nos widgets dos forms

---

## 13. Regras de Negocio - Controle de Estoque

O campo `stock_active` NAO define se o produto esta ativo/inativo. Ele controla se o produto tem **producao limitada** (controle de estoque).

### Semantica dos campos:
- `stock_active=False` — Producao continua. Produto sempre disponivel.
- `stock_active=True` — Producao limitada. Quantidade controlada por `stock_quantity`.
- `stock_active=True` + `stock_quantity=0` — Produto esgotado.

### Exibicao na listagem:
| Estado | Badge | Cor |
|--------|-------|-----|
| `stock_active=False` | "Continuo" | Azul |
| `stock_active=True`, `quantity > 0` | "X unidades" | Verde |
| `stock_active=True`, `quantity = 0` | "Esgotado" | Vermelho |

### Comportamento no envio por categoria:
Produtos com `stock_active=True` e `stock_quantity=0` (esgotados) sao **automaticamente pulados** no envio de mensagens por categoria. Produtos com producao continua (`stock_active=False`) sao sempre enviados.

### Validacao de preco:
O preco deve ser **maior que zero** — tanto no frontend (validacao JS) quanto no backend (`clean_price`).

---

## 14. Observacoes e Pontos de Atencao

### Webhook sem autenticacao
O endpoint `/messages/hook` e `@csrf_exempt` mas valida o IP de origem contra `EVOLUTION_SERVER_IP`. Apenas requisicoes do servidor da Evolution API sao aceitas.

### Tratamento de erros no envio de categoria
Quando o envio de mensagem por categoria falha para produtos individuais, o sistema conta as falhas e retorna status HTTP adequado: 200 (todos enviados), 207 (envio parcial) ou 500 (todos falharam).

### Listagem de produtos
A listagem de produtos (`products.html`) e renderizada inteiramente via JavaScript/API. A view `get_all_products` apenas renderiza o template vazio — todos os dados sao carregados via `api_list_products`.

### Template unificado de produto
Os formularios de criacao e edicao de produto usam um unico template (`product_form.html`). Variaveis de contexto (`is_edit`, `page_title`, `submit_label`) controlam o comportamento. No modo edicao, o formulario exibe preview da imagem atual.

### Ausencia de testes
Os arquivos `tests.py` em todos os apps estao vazios. Nao ha testes automatizados implementados.
