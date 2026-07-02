## Why

O AutoSell hoje é um monólito Django que mistura renderização de páginas (templates + Tailwind CDN + Vanilla JS) e lógica de negócio/API no mesmo repositório. Isso acopla o ciclo de vida do frontend ao do backend, dificulta escalar cada camada de forma independente e limita a evolução da UI. A meta é separar em **dois repositórios independentes**: um **frontend em React** (SPA) e um **backend em Java** (Spring Boot), preservando integralmente o comportamento funcional atual (catálogo, contatos, WhatsApp, live chat, carrinho e vendas).

## What Changes

- **BREAKING**: O backend Django (`autosell/`, apps `products`, `categories`, `contacts`, `wppmessages`, `livechat`, `systemlogs`, `dashboard`) é **reescrito em Java com Spring Boot** e passa a viver em um repositório próprio (`autosell-backend`).
- **BREAKING**: A camada de apresentação (templates Django + Vanilla JS) é **substituída por uma SPA React** (Vite + TypeScript + Tailwind) em um repositório próprio (`autosell-frontend`), consumindo o backend apenas via API JSON.
- **BREAKING**: A autenticação deixa de ser baseada em sessão de template Django e passa a ser uma API de autenticação consumida pelo frontend (cookie de sessão HttpOnly emitido pelo backend Spring, sem mudança de modelo de usuário para o usuário final).
- Todos os endpoints JSON existentes são reimplementados em Java mantendo o **mesmo contrato de rota, método e formato de resposta** (`data` / `status` / `page` / `stats`) documentado na seção 4 do CLAUDE.md.
- O webhook da Evolution API (`/livechat/hook/`, `/messages/hook/`) é reimplementado em Java preservando validação por IP, detecção de eco, merge de contatos LID/JID e atualização de status.
- Integrações externas (Evolution API e MinIO S3) são reimplementadas com SDKs Java equivalentes, mantendo os mesmos contratos e caminhos de armazenamento.
- O banco de dados **PostgreSQL de produção é preservado**: o esquema é mapeado 1:1 via JPA/Hibernate para garantir migração sem perda de dados (mesmas tabelas, colunas e índices).
- Novas ferramentas de build/deploy por repositório (Maven/Gradle no backend, Vite/npm no frontend), com configuração via variáveis de ambiente equivalentes às atuais.
- **Non-goal**: Não há mudança de requisitos funcionais nem de regras de negócio (estoque, normalização de telefone, transação atômica de venda permanecem idênticos). Não há mudança de banco de produção nem de instância WhatsApp.

## Capabilities

### New Capabilities
- `backend-platform`: Fundação do backend Java/Spring Boot — estrutura de projeto, configuração por ambiente, contrato de resposta JSON padronizado, tratamento de erros/logging (equivalente a `SystemLog`), autenticação por sessão e CORS.
- `catalog-management`: Gestão de produtos e categorias — CRUD, regras de estoque (contínuo/limitado/esgotado), relacionamento M2M, upload de imagens.
- `contact-management`: Gestão de contatos — CRUD, normalização de telefone (55XXXXXXXXXXX), identidade LID/JID do WhatsApp.
- `whatsapp-integration`: Integração com a Evolution API — envio de texto/mídia, envio em massa de produto/categoria/catálogo, formatação de mensagens, download de mídia para o MinIO.
- `live-chat`: Chat ao vivo — conversas, mensagens, ingestão via webhook (eco, merge de contatos, atualização de status), atualizações por polling.
- `sales-and-cart`: Carrinho e vendas — itens com snapshot de preço, checkout em transação atômica com dedução de estoque, venda rápida e histórico imutável de vendas.
- `web-client`: SPA React — roteamento, consumo de API, fluxo de login, design system (dark mode, padrões de loading UX, zero-scroll) reproduzindo a experiência atual.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ — este é o primeiro conjunto de specs do projeto. -->

## Impact

- **Repositórios**: cria `autosell-frontend` (React) e `autosell-backend` (Java); o repositório atual Django é congelado/arquivado após a virada.
- **Código afetado**: todo o código Python (`*/views.py`, `*/api_views.py`, `*/models.py`, `*/forms.py`, `utils/evoapi.py`, `utils/storage.py`, `utils/api_response.py`, `livechat/webhook.py`) e todos os templates Django.
- **APIs**: todas as rotas de `products`, `categories`, `contacts`, `messages` e `livechat` (incluindo carrinho, polling e webhooks) são reimplementadas mantendo contrato.
- **Dependências**: Django/DRF-like stack → Spring Boot (Web, Data JPA, Security), driver PostgreSQL, cliente MinIO/S3, cliente HTTP (Evolution API); frontend passa a depender de Node/Vite/React.
- **Infraestrutura**: dois artefatos de deploy (imagem/container do backend Java e build estático do frontend), configuração de CORS entre domínios, roteamento de webhook para o novo backend.
- **Dados**: PostgreSQL de produção reutilizado; exige mapeamento fiel do esquema e validação de integridade pós-migração.
- **Riscos**: paridade de comportamento do webhook (LID/JID, eco, merge), fidelidade do contrato de API e reprodução da UX do frontend.
