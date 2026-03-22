# AutoSell - Base de Conhecimento do Agente

> Este documento e a base de conhecimento centralizada do projeto AutoSell.
> Todo agente Claude Code deve ler este arquivo antes de qualquer tarefa.

---

## 1. Visao Geral do Projeto

**AutoSell** e uma plataforma de comercio via WhatsApp construida com Django. Permite gerenciar produtos, categorias, contatos e realizar vendas diretamente pelo WhatsApp atraves de um painel web com live chat integrado.

| Item | Valor |
|------|-------|
| Linguagem | Python 3.13 |
| Framework | Django 5.2.5 |
| Frontend | Templates Django + Tailwind CSS (CDN) + Vanilla JS |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL (89.116.225.222:45555) |
| Storage | MinIO S3-compatible |
| WhatsApp | Evolution API v2.1.1 |
| Dominio | autosell.upperlavtech.com |
| Timezone | America/Sao_Paulo |
| Idioma | pt-br |
| Auth | Django session-based (nativo) |

---

## 2. Estrutura de Diretorios

```
autosell/
├── autosell/              # Configuracao Django (settings, urls, wsgi/asgi)
├── dashboard/             # App - Pagina inicial (view unica)
├── products/              # App - CRUD de Produtos
├── categories/            # App - CRUD de Categorias (M2M com Product)
├── contacts/              # App - CRUD de Contatos
├── wppmessages/           # App - Envio de mensagens WhatsApp (bulk)
├── livechat/              # App - Chat ao vivo + Carrinho + Vendas
├── systemlogs/            # App - Logs centralizados (admin only)
├── utils/                 # Modulo utilitario
│   ├── evoapi.py          # Integracao Evolution API
│   ├── storage.py         # Upload/delete MinIO
│   └── api_response.py    # Helpers de resposta + logging
├── templates/             # Templates globais (login)
├── docs/                  # Documentacao
│   ├── DOCUMENTACAO.md            # Doc tecnica completa (PT-BR)
│   ├── autosell-complete-style-guide.md  # Design system + frontend
│   └── evolution-api-v2-reference.md     # Referencia Evolution API
├── media/                 # Arquivos de midia (nao versionado)
├── requirements.txt       # Dependencias Python
├── manage.py              # Django CLI
└── .env                   # Variaveis de ambiente (nao versionado)
```

**Cada app segue o padrao:**
- `models.py` - Modelos de dados
- `views.py` - Views HTML (templates)
- `api_views.py` - Endpoints JSON (API)
- `forms.py` - Validacao de formularios
- `urls.py` - Roteamento
- `admin.py` - Config do Django Admin
- `templates/` - Templates HTML

---

## 3. Modelos de Dados

### Product (`products/models.py`)
| Campo | Tipo | Regras |
|-------|------|--------|
| name | CharField(90) | Obrigatorio, 4-90 chars |
| description | TextField(255) | Opcional |
| price | DecimalField(10,2) | Obrigatorio, > 0 |
| image_url | CharField(500) | URL no MinIO |
| stock_active | BooleanField | Default: False |
| stock_quantity | IntegerField | Default: 0, reset a 0 se stock_active=False |
| updated_at | DateTimeField | auto_now |
| created_at | DateTimeField | auto_now_add |

**Regra de negocio (estoque):**
- `stock_active=False` → Producao continua (sempre disponivel)
- `stock_active=True` → Producao limitada (controlado por stock_quantity)
- `stock_active=True + stock_quantity=0` → Esgotado (excluido de envios de categoria)
- Badges no frontend: "Continuo" (azul), "X unidades" (verde), "Esgotado" (vermelho)

### Category (`categories/models.py`)
| Campo | Tipo | Regras |
|-------|------|--------|
| name | CharField(90) | Obrigatorio |
| description | TextField(255) | Opcional |
| image_url | CharField(500) | URL no MinIO |
| products | ManyToManyField(Product) | related_name='categories' |
| updated_at / created_at | DateTimeField | auto |

### Contact (`contacts/models.py`)
| Campo | Tipo | Regras |
|-------|------|--------|
| name | CharField(60) | Obrigatorio, 3-60 chars |
| lid | CharField(50) | Unique, indexed - LID do WhatsApp (remoteJid) |
| phone | CharField(20) | Unique, indexed - Telefone formato 55XXXXXXXXXXX |
| updated_at / created_at | DateTimeField | auto |

**Regra de normalizacao de telefone:**
- Remove caracteres especiais: `(`, `)`, `-`, espaco, `+`
- Se 11 digitos → adiciona prefixo `55`
- Formato final: 13 digitos `55XXXXXXXXXXX`

### Conversation (`livechat/models.py`)
| Campo | Tipo | Regras |
|-------|------|--------|
| contact | OneToOneField(Contact) | CASCADE |
| remote_jid | CharField(50) | Unique, indexed |
| last_message_text | CharField(200) | Preview da ultima msg |
| last_message_at | DateTimeField | Indexed, ordenacao |
| last_message_direction | CharField(3) | 'in' ou 'out' |
| unread_count | IntegerField | Default: 0 |

### ChatMessage (`livechat/models.py`)
| Campo | Tipo | Regras |
|-------|------|--------|
| contact | ForeignKey(Contact) | CASCADE |
| conversation | ForeignKey(Conversation) | CASCADE |
| remote_jid | CharField(50) | Indexed |
| wpp_message_id | CharField(100) | Unique - ID do WhatsApp |
| direction | CharField(3) | 'in' (recebida) / 'out' (enviada) |
| msg_type | CharField(20) | text, product, category, catalog, image, audio |
| content | TextField | Conteudo textual |
| media_url | URLField(500) | URL da midia no MinIO |
| product | ForeignKey(Product) | SET_NULL, opcional |
| category | ForeignKey(Category) | SET_NULL, opcional |
| status | CharField(20) | pending → sent → delivered → read / failed |
| timestamp | DateTimeField | Indexed |

### Cart e CartItem (`livechat/models.py`)
- **Cart**: conversation FK, contact FK, status (open/finalized/cancelled), finalized_at
- **CartItem**: cart FK, product FK, quantity, unit_price (snapshot do preco)
- Unique together: (cart, product) - produto nao duplica no carrinho

### Sale e SaleItem (`livechat/models.py`)
- **Sale**: contact FK, cart FK (opcional), total, created_at
- **SaleItem**: sale FK, product FK (SET_NULL), product_name (snapshot), quantity, unit_price
- Sale e imutavel - registro permanente da transacao

### Message (`wppmessages/models.py`)
- Registro de envios bulk (fora do contexto de conversa)
- type: 'product' ou 'category'
- status: pending → sent / failed

### SystemLog (`systemlogs/models.py`)
- level: INFO, WARNING, ERROR, CRITICAL
- source, message, trace, request_method, request_path, user
- Usado via `log_system_event()` em `utils/api_response.py`

---

## 4. Endpoints da API

### Formato padrao de resposta
```json
{
  "data": [...],
  "status": { "code": 200, "message": "..." },
  "page": { "current": 1, "per_page": 10, "total_items": 100, "total_pages": 10 },
  "stats": { ... }
}
```

### Rotas Principais (`autosell/urls.py`)
| Rota | Destino |
|------|---------|
| `/` | Dashboard |
| `/admin/` | Django Admin |
| `/products/` | App products |
| `/categories/` | App categories |
| `/contacts/` | App contacts |
| `/messages/` | App wppmessages |
| `/livechat/` | App livechat |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |

### Products API (`products/urls.py`)
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/products/api/` | Listar (paginado, busca, stats) |
| POST | `/products/api/create/` | Criar produto |
| POST | `/products/api/<id>/edit/` | Editar produto |
| POST | `/products/api/<id>/delete/` | Deletar produto |

### Categories API (`categories/urls.py`)
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/categories/api/` | Listar com contagem de produtos |
| POST | `/categories/api/create/` | Criar categoria |
| POST | `/categories/api/<id>/edit/` | Editar categoria |
| POST | `/categories/api/<id>/delete/` | Deletar categoria |
| POST | `/categories/api/<id>/remove-product/<pid>/` | Remover produto |

### Contacts API (`contacts/urls.py`)
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/contacts/api/` | Listar com message_count |
| POST | `/contacts/api/create/` | Criar contato |
| POST | `/contacts/api/<id>/edit/` | Editar contato |
| POST | `/contacts/api/<id>/delete/` | Deletar contato |

### WhatsApp Messages API (`wppmessages/urls.py`)
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/messages/api/` | Listar mensagens enviadas |
| POST | `/messages/api/send/` | Enviar produto/categoria |
| POST | `/messages/hook/` | Webhook (Evolution API) |

### LiveChat API (`livechat/urls.py`)

**Conversas:**
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/livechat/api/conversations/` | Listar conversas |
| GET | `/livechat/api/conversations/<id>/messages/` | Mensagens da conversa |
| POST | `/livechat/api/conversations/<id>/send-text/` | Enviar texto |
| POST | `/livechat/api/conversations/<id>/send-product/` | Enviar produto |
| POST | `/livechat/api/conversations/<id>/send-category/` | Enviar categoria |
| POST | `/livechat/api/conversations/<id>/send-catalog/` | Enviar catalogo completo |
| POST | `/livechat/api/conversations/<id>/mark-read/` | Marcar como lida |
| POST | `/livechat/api/conversations/<id>/update-contact/` | Atualizar contato |
| POST | `/livechat/api/conversations/start/` | Iniciar conversa |
| POST | `/livechat/api/conversations/<id>/delete/` | Deletar conversa |

**Carrinho:**
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/livechat/api/conversations/<id>/cart/` | Ver carrinho |
| POST | `/livechat/api/conversations/<id>/cart/add/` | Adicionar item |
| POST | `/livechat/api/conversations/<id>/cart/update/` | Atualizar quantidade |
| POST | `/livechat/api/conversations/<id>/cart/remove/<item_id>/` | Remover item |
| POST | `/livechat/api/conversations/<id>/cart/finalize/` | Finalizar (criar venda) |
| POST | `/livechat/api/conversations/<id>/cart/clear/` | Cancelar carrinho |

**Outros:**
| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/livechat/api/conversations/<id>/quick-sell/` | Venda rapida (sem carrinho) |
| GET | `/livechat/api/poll/?since=<ISO>` | Polling global de atualizacoes |
| GET | `/livechat/api/products/` | Buscar produtos (exclui esgotados) |
| GET | `/livechat/api/categories/` | Listar categorias |
| POST | `/livechat/hook/` | Webhook (Evolution API) |

---

## 5. Integracoes Externas

### 5.1 Evolution API (WhatsApp)

**Arquivo:** `utils/evoapi.py`

**Documentacao oficial:** https://doc.evolution-api.com
**Referencia local:** `docs/evolution-api-v2-reference.md`

**Configuracao (.env):**
- `EVOLUTION_URL` - URL base da API
- `EVOLUTION_TOKEN` - Token global
- `EVOLUTION_INSTANCE_ID` - Nome da instancia (AutoSell)
- `EVOLUTION_INSTANCE_TOKEN` - Token da instancia
- `EVOLUTION_SERVER_IP` - IP do servidor (validacao webhook)

**Funcoes principais:**

| Funcao | Endpoint Evolution | Descricao |
|--------|-------------------|-----------|
| `send_text_message(number, text)` | POST `/message/sendText/{instance}` | Envia texto |
| `send_media_message(number, mediatype, mimetype, caption, media, fileName)` | POST `/message/sendMedia/{instance}` | Envia imagem/video/doc |
| `get_base64_from_media_message(webhook_data, convert_to_mp4)` | POST `/chat/getBase64FromMediaMessage/{instance}` | Baixa midia de msg recebida |
| `mark_message_as_read(remote_jid, message_ids)` | POST `/chat/markMessageAsRead/{instance}` | Marca como lida |
| `send_presence(number, presence)` | POST `/chat/sendPresence/{instance}` | Indicador "digitando" |
| `build_product_text(product)` | - | Formata texto do produto |
| `build_catalog_text(products_by_category, uncategorized)` | - | Formata catalogo completo |
| `resolve_contact_number(contact)` | - | Retorna phone (JID) ou lid |
| `resolve_conversation_number(conversation)` | - | Prioriza phone sobre remote_jid |

**Comportamento LID vs JID (CRITICO):**
- `key.remoteJid` chega como LID (nao telefone, apesar da doc da API)
- `key.senderPn` contem o JID real (telefone) - APENAS em fromMe=false
- `pushName` confiavel apenas quando fromMe=false
- Mensagens fromMe=true criam contato apenas com LID (sem telefone inicialmente)
- Telefone e populado quando contato envia mensagem (fromMe=false)

### 5.2 MinIO (Storage S3)

**Arquivo:** `utils/storage.py`

**Documentacao oficial:** https://min.io/docs/minio/linux/index.html
**Django Storages:** https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

**Configuracao (.env):**
- `MINIO_SERVER_URL` - Endpoint MinIO
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` - Credenciais
- `BUCKET_NAME` - Bucket (autosell)

**Extensoes permitidas:** `.jpg, .jpeg, .png, .gif, .webp, .mp3, .ogg, .opus, .m4a, .aac`

**Funcoes:**
| Funcao | Descricao |
|--------|-----------|
| `upload_file(file_name, file)` | Upload de arquivo, retorna URL |
| `upload_media_from_base64(file_name, base64_data)` | Upload de midia base64 |
| `upload_media_from_url(file_name, url)` | Download + upload de URL |
| `delete_file(file_url)` | Deleta arquivo do MinIO |
| `clean_file_name(file_name)` | Sanitiza nome (remove acentos/especiais) |

**Paths de armazenamento:**
- Produtos: `products/{uuid}.ext`
- Categorias: `categories/{uuid}.ext`
- Midia do chat: `chat_media/{type}_{uuid}.ext`

---

## 6. Webhook (Evolution API → AutoSell)

**Arquivo:** `livechat/webhook.py`
**Rota:** `POST /livechat/hook/`

### Validacao
- IP whitelist: `EVOLUTION_SERVER_IP`, `127.0.0.1`, `::1`, `172.18.0.1`, `10.11.0.4`
- CSRF exempt (API externa)
- Eventos aceitos: `messages.upsert`, `messages.update`

### Fluxo de Mensagem Recebida (`messages.upsert`)

```
1. Extrair mensagem do payload Evolution API
2. Detectar direcao: fromMe=true (saida) / fromMe=false (entrada)
3. Extrair texto de: conversation → extendedTextMessage.text
4. Detectar tipo de midia: image, audio, video, document, sticker, contact, location
5. Download de midia para MinIO (prioridade):
   a. Evolution API getBase64FromMediaMessage (mais confiavel)
   b. Campo base64 no payload do webhook
   c. mediaUrl (se S3 configurado na Evolution)
   d. jpegThumbnail (fallback baixa qualidade, apenas imagens)
6. Encontrar/criar contato:
   - lid = remoteJid.split('@')[0]
   - phone = senderPn ou remoteJidAlt (apenas incoming)
   - Se conflito (lid e phone apontam para contatos diferentes) → MERGE
7. Deteccao de eco: Se fromMe=true e conteudo bate com msg pending dos ultimos 30s
   → Atualiza wpp_message_id na msg original (nao cria duplicata)
8. Criar/atualizar Conversation e ChatMessage
9. Atualizar last_message_text, last_message_at, unread_count
```

### Merge de Contatos
Quando lid e phone apontam para contatos diferentes:
- ID menor = primario, ID maior = secundario
- Move mensagens, carrinhos, vendas do secundario para primario
- Enriquece primario com dados do secundario
- Deleta secundario

### Atualizacao de Status (`messages.update`)
| Codigo | Status |
|--------|--------|
| 2 | sent |
| 3 | delivered |
| 4 | read |
| 5 | read (played) |

- Status so avanca (nunca retrocede)
- Tambem aceita strings: SERVER_ACK, DELIVERY_ACK, READ, PLAYED

---

## 7. Fluxos de Negocio

### Carrinho → Venda (Transacao Atomica)
```
1. Adicionar itens ao carrinho (snapshot de preco)
2. POST cart/finalize/ → BEGIN ATOMIC TRANSACTION
3. Para cada CartItem:
   - Se product.stock_active=true: Deduz stock_quantity com F() (race-condition safe)
   - Se estoque insuficiente: ROLLBACK completo
4. Cria Sale com total calculado
5. Cria SaleItem para cada item (com snapshot de dados)
6. Cart.status = 'finalized'
7. COMMIT
```

### Venda Rapida (Quick Sell)
- Compra direta de produto unico sem carrinho
- Mesma logica atomica de deducao de estoque
- Cria Sale + SaleItem diretamente

### Envio de Produto
```
1. Resolve numero do contato (phone ou lid)
2. Se produto tem imagem → send_media_message (imagem + texto formatado)
3. Se nao tem imagem → send_text_message (texto formatado)
4. Formato: *Nome*\n_Descricao_\n\n*Restam:* X\n*Preco:* R$ XX.XX
```

### Envio de Categoria
```
1. Busca produtos da categoria
2. Exclui produtos esgotados (stock_active=True + stock_quantity=0)
3. Envia cada produto individualmente (sequencial)
4. Retorna: 200 (todos OK), 207 (parcial), 500 (todos falharam)
```

### Envio de Catalogo
```
1. Agrupa produtos por categoria
2. Exclui esgotados
3. Formata texto com headers de categoria (emoji)
4. Inclui produtos sem categoria
5. Envia como mensagem de texto unica
```

---

## 8. Seguranca

- **Autenticacao:** `@login_required` em todas as views/APIs (exceto webhook)
- **Webhook:** Validado por IP (sem CSRF)
- **CORS:** Configurado para dominios especificos
- **CSRF:** Habilitado globalmente (exceto webhook)
- **XSS:** `escapeHtml()` em JS para dados dinamicos
- **Validacao:** Inputs validados em formularios e APIs
- **Secrets:** Via `.env` com `python-decouple`
- **Storage:** MinIO externo (nao no web root)
- **Paginacao:** max 100 items por pagina

---

## 9. Frontend e Design System

**Guia completo:** `docs/autosell-complete-style-guide.md`

### Principios
- Minimalismo funcional
- Zero Scroll Policy (100% viewport, sem scroll vertical)
- Mobile-first responsive
- Dark mode (class-based, localStorage)

### Stack Frontend
- Tailwind CSS via CDN
- Vanilla JavaScript (sem frameworks JS)
- Templates Django com heranca
- Dados carregados via API (fetch) com UX de loading

### Padrao de Loading UX (Obrigatorio)
1. Skeleton shimmer inline nos stat cards
2. Loading placeholder (spinner + "Carregando...") nos containers
3. Content fade-in apos resposta da API (0.3s)
4. Numeros animados nos stat cards (0.6s ease-out cubic)
5. Nunca gerar skeleton rows falsos
6. Usar `overflow-hidden` (nunca `overflow-y-auto`)

### Dark Mode
- `darkMode: 'class'` no Tailwind config
- Persiste em `localStorage('darkMode')`
- Script no `<head>` previne FOUC
- Toggle por botao na interface

### Breakpoints
| Nome | Largura | Dispositivo |
|------|---------|-------------|
| default | <640px | Smartphones |
| sm | >=640px | Celulares grandes |
| md | >=768px | Tablets |
| lg | >=1024px | Desktops |
| xl | >=1280px | Telas grandes |

### Funcoes JS Globais (definidas em dashboard.html)
- `animateNumber(el, endValue, opts)` - Anima contadores
- `loadingPlaceholder()` - Retorna HTML de loading
- `applyFadeIn(el)` - Aplica animacao de fade
- `showToast(msg, type, duration)` - Notificacao toast
- `confirmModal(opts)` - Modal de confirmacao (Promise)
- `setButtonLoading(btn, loading, text)` - Estado de loading em botao

### Overflow de Texto (OBRIGATORIO)
- Desktop: `truncate` com container de icone, `min-w-0 flex-1` para texto
- Mobile: `truncate` em titulos, `line-clamp-2` para descricoes
- SEMPRE adicionar atributo `title` com texto completo
- Nunca permitir texto quebrar layout

---

## 10. Dependencias (requirements.txt)

| Pacote | Versao | Uso |
|--------|--------|-----|
| Django | 5.2.5 | Framework web |
| django-cors-headers | 4.3.1 | CORS |
| psycopg2-binary | 2.9.10 | Adaptador PostgreSQL |
| python-decouple | 3.8 | Variaveis de ambiente |
| requests | 2.32.5 | Chamadas HTTP |
| django-storages[s3] | 1.14.4 | Backend MinIO/S3 |
| pydantic | 2.11.7 | Validacao de dados |
| channels / websockets | - | WebSocket support |

---

## 11. Variaveis de Ambiente (.env)

| Variavel | Descricao |
|----------|-----------|
| `PROD` | True/False - modo producao |
| `SECRET_KEY` | Chave secreta Django |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL (apenas prod) |
| `SITE_URL` | URL base do site |
| `EVOLUTION_URL` | URL da Evolution API |
| `EVOLUTION_TOKEN` | Token global da Evolution |
| `EVOLUTION_INSTANCE_ID` | Nome da instancia WhatsApp |
| `EVOLUTION_INSTANCE_TOKEN` | Token da instancia |
| `EVOLUTION_SERVER_IP` | IP do servidor (validacao webhook) |
| `MINIO_SERVER_URL` | Endpoint MinIO |
| `MINIO_ROOT_USER` | Usuario MinIO |
| `MINIO_ROOT_PASSWORD` | Senha MinIO |
| `BUCKET_NAME` | Bucket no MinIO |

---

## 12. Convencoes e Padroes do Projeto

### Codigo
- Idioma do codigo: Ingles (variaveis, funcoes, classes)
- Idioma da interface: Portugues (PT-BR)
- Todas APIs retornam JSON no formato padrao (secao 4)
- Erros logados via `log_system_event()` → SystemLog
- Exceptions capturadas via `api_exception()` que loga e retorna 500
- Forms usam `api_form_error()` para erros de campo

### Git
- Branch principal: `main`
- Mensagens de commit: `tipo - Descricao` (ex: `feature - Envio de catalogo`, `fix - Correcao de img`)

### Banco de Dados
- Migrations via Django ORM
- Nao usar raw SQL
- F() expressions para operacoes atomicas (ex: deducao de estoque)
- select_for_update quando necessario

### Testes
- Arquivos `tests.py` existem mas estao vazios (sem testes implementados)
- Sem CI/CD configurado

---

## 13. Links de Referencia

| Recurso | Link |
|---------|------|
| Evolution API Docs | https://doc.evolution-api.com |
| Evolution API Reference (local) | `docs/evolution-api-v2-reference.md` |
| Django Docs | https://docs.djangoproject.com/en/5.2/ |
| Tailwind CSS | https://tailwindcss.com/docs |
| MinIO Docs | https://min.io/docs/minio/linux/index.html |
| Django Storages (S3) | https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html |
| Doc Tecnica Completa | `docs/DOCUMENTACAO.md` |
| Style Guide Frontend | `docs/autosell-complete-style-guide.md` |

---

## 14. Decisoes Tecnicas e Contexto

1. **Tailwind via CDN** (nao compilado): Simplicidade de deploy, sem build step
2. **Vanilla JS** (sem React/Vue): Projeto simples, sem necessidade de SPA
3. **Django Templates + API**: Paginas carregam via template, dados via fetch JS (hibrido)
4. **MinIO para storage**: S3-compatible, hospedado junto na infra (Easypanel)
5. **Evolution API**: Alternativa open-source ao WhatsApp Business API oficial
6. **Sem WebSocket real-time**: Polling via `/livechat/api/poll/` (simplicidade)
7. **Contact merge automatico**: Necessario porque Evolution API usa LID e JID separadamente
8. **Snapshot de preco no carrinho**: Preco do produto pode mudar apos adicionar ao carrinho
9. **Snapshot de nome na venda**: Produto pode ser deletado mas venda mantem historico

---

## 15. Avisos para o Agente

- **NUNCA** commitar o arquivo `.env` (contem credenciais)
- **NUNCA** alterar migrations manualmente - usar `makemigrations`
- **SEMPRE** testar endpoints com `@login_required`
- **SEMPRE** usar `api_exception()` para tratar erros em API views
- **SEMPRE** sanitizar nomes de arquivo antes de upload (`clean_file_name`)
- **SEMPRE** normalizar telefone para formato 55XXXXXXXXXXX
- **CUIDADO** com stock_active: NAO significa ativo/inativo, significa PRODUCAO LIMITADA
- **CUIDADO** com LID vs JID: senderPn so e confiavel em fromMe=false
- **PREFERIR** editar arquivos existentes em vez de criar novos
- **SEGUIR** o padrao de loading UX ao criar novas paginas
- **SEGUIR** o style guide para qualquer alteracao frontend
