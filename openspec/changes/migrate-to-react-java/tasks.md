## 1. Preparação e baseline de dados

- [ ] 1.1 Introspectar o schema PostgreSQL atual e documentar tabelas, colunas, índices e constraints de cada app Django
- [ ] 1.2 Criar dump de produção e restaurar em um banco de staging isolado
- [ ] 1.3 Congelar e documentar o contrato de API atual (rotas, métodos, envelope `data`/`status`/`page`/`stats`) a partir do CLAUDE.md e do código Django
- [ ] 1.4 Capturar payloads reais de webhook da Evolution API (`messages.upsert` e `messages.update`, com e sem mídia, fromMe true/false) para testes de paridade

## 2. Repositório e fundação do backend Java (`backend-platform`)

- [x] 2.1 Criar o repositório `autosell-backend` com Spring Boot 3.x, Java 21 e build Maven <!-- gerado via Spring Initializr; Boot 4.1 (default atual), nao 3.x -->
- [x] 2.2 Estruturar pacotes por domínio (`platform`, `catalog`, `contact`, `whatsapp`, `livechat`, `sales`) espelhando os apps Django
- [x] 2.3 Configurar leitura de variáveis de ambiente equivalentes ao `.env` (DB, Evolution, MinIO, SITE_URL, SECRET) com falha clara se faltarem obrigatórias
- [x] 2.4 Configurar JPA/Hibernate com `ddl-auto=validate` apontando para o banco de staging
- [x] 2.5 Implementar o envelope de resposta JSON padrão (`data`/`status`/`page`/`stats`) e helpers de paginação (máx. 100 por página)
- [x] 2.6 Implementar tratamento centralizado de exceções + logging estruturado equivalente a `SystemLog` (nível, origem, mensagem, trace, método, path, usuário)
- [x] 2.7 Configurar CORS restrito ao domínio do frontend com suporte a credenciais

## 3. Autenticação (`backend-platform`)

- [ ] 3.1 Configurar Spring Security com sessão e cookie HttpOnly; proteger todos os endpoints exceto webhooks
- [ ] 3.2 Implementar `PasswordEncoder` compatível com `pbkdf2_sha256` do Django (ou plano de reset de senha na virada)
- [ ] 3.3 Implementar endpoints de login e logout consumíveis pela SPA
- [ ] 3.4 Configurar CSRF para requisições mutantes do frontend e isenção para webhooks

## 4. Integrações externas (clientes anticorrupção)

- [ ] 4.1 Implementar `StorageService` (MinIO/S3): upload de arquivo/base64/url, delete, sanitização de nome e caminhos (`products/`, `categories/`, `chat_media/`)
- [ ] 4.2 Implementar `EvolutionClient`: sendText, sendMedia, getBase64FromMediaMessage, markMessageAsRead, sendPresence
- [ ] 4.3 Portar formatação de mensagens: `build_product_text` e `build_catalog_text`
- [ ] 4.4 Portar resolução de número: prioridade `phone` (JID) sobre `lid`/`remote_jid`

## 5. Catálogo (`catalog-management`)

- [ ] 5.1 Mapear entidades JPA `Product` e `Category` (M2M) para as tabelas existentes
- [ ] 5.2 Implementar CRUD de produtos com validação (nome 4-90, preço > 0) e listagem paginada com busca e stats
- [ ] 5.3 Implementar regras de estoque (contínuo/limitado/esgotado; zerar quantidade quando `stock_active=false`)
- [ ] 5.4 Implementar CRUD de categorias com contagem de produtos e remoção de produto da categoria
- [ ] 5.5 Implementar upload de imagem de produto/categoria via `StorageService` com validação de extensão

## 6. Contatos (`contact-management`)

- [ ] 6.1 Mapear entidade JPA `Contact` (com `lid` e `phone` únicos e indexados)
- [ ] 6.2 Implementar CRUD de contatos com validação (nome 3-60) e listagem com contagem de mensagens
- [ ] 6.3 Implementar normalização de telefone (limpeza de caracteres, prefixo 55, formato `55XXXXXXXXXXX`)

## 7. WhatsApp / envios em massa (`whatsapp-integration`)

- [ ] 7.1 Mapear entidade JPA `Message` (envios em massa: type/status)
- [ ] 7.2 Implementar envio de produto individual (mídia com legenda ou texto)
- [ ] 7.3 Implementar envio de categoria (sequencial, excluindo esgotados, com retorno 200/207/500)
- [ ] 7.4 Implementar envio de catálogo agrupado por categoria + sem categoria
- [ ] 7.5 Reimplementar o endpoint de webhook de mensagens (`/messages/hook/`) mantendo contrato

## 8. Live chat (`live-chat`)

- [ ] 8.1 Mapear entidades JPA `Conversation` e `ChatMessage` para as tabelas existentes
- [ ] 8.2 Implementar endpoints de conversas (listar, mensagens, enviar texto/produto/categoria/catálogo, marcar lida, atualizar contato, iniciar, excluir)
- [ ] 8.3 Implementar ingestão de `messages.upsert` (extração de texto/mídia, download com prioridade getBase64→base64→mediaUrl→jpegThumbnail)
- [ ] 8.4 Implementar resolução/criação de contato por `lid` e `phone` (senderPn), incluindo contato só com LID
- [ ] 8.5 Implementar detecção de eco (fromMe=true correspondendo a mensagem `pending` dos últimos 30s)
- [ ] 8.6 Implementar merge de contatos (menor ID primário; mover mensagens/carrinhos/vendas; excluir secundário)
- [ ] 8.7 Implementar atualização de status via `messages.update` (2/3/4/5 e strings; nunca retrocede)
- [ ] 8.8 Implementar validação de webhook por whitelist de IP e isenção de CSRF
- [ ] 8.9 Implementar endpoint de polling (`/livechat/api/poll/?since=<ISO>`)

## 9. Carrinho e vendas (`sales-and-cart`)

- [ ] 9.1 Mapear entidades JPA `Cart`, `CartItem`, `Sale`, `SaleItem` (unique cart+product; snapshots)
- [ ] 9.2 Implementar operações de carrinho (ver, adicionar com snapshot de preço, atualizar quantidade, remover, limpar)
- [ ] 9.3 Implementar checkout atômico com dedução segura de estoque (UPDATE condicional) e rollback em estoque insuficiente
- [ ] 9.4 Implementar venda rápida (quick-sell) com a mesma lógica atômica
- [ ] 9.5 Garantir imutabilidade da venda e snapshot de nome/preço nos itens

## 10. Testes de paridade do backend

- [ ] 10.1 Escrever testes de contrato comparando respostas das rotas Django vs Java no banco de staging
- [ ] 10.2 Escrever testes do webhook usando os payloads capturados (eco, merge, status, mídia)
- [ ] 10.3 Escrever teste de concorrência da dedução de estoque (finalizações simultâneas)

## 11. Repositório e fundação do frontend React (`web-client`)

- [x] 11.1 Criar o repositório `autosell-frontend` com Vite + React + TypeScript
- [x] 11.2 Configurar Tailwind com `darkMode: 'class'` reproduzindo o design system e prevenção de FOUC
- [x] 11.3 Configurar React Router e cliente de API (fetch com `withCredentials`) + TanStack Query
- [x] 11.4 Implementar funções/utilitários de UX globais (animateNumber, loadingPlaceholder, fadeIn, toast, confirmModal, botão loading)

## 12. Telas do frontend (`web-client`)

- [ ] 12.1 Implementar fluxo de login/logout e guarda de rotas para não autenticados
- [ ] 12.2 Implementar dashboard com stat cards animados e loading UX
- [ ] 12.3 Implementar telas de produtos e categorias (CRUD, badges de estoque, upload de imagem)
- [ ] 12.4 Implementar tela de contatos (CRUD, contagem de mensagens)
- [ ] 12.5 Implementar tela de mensagens/envios em massa (produto/categoria)
- [ ] 12.6 Implementar live chat (lista de conversas, mensagens, envio, mídia, carrinho, venda) com polling
- [ ] 12.7 Aplicar responsividade, zero-scroll e truncamento/tooltip de textos longos em todas as telas

## 13. Deploy e cutover

- [ ] 13.1 Criar artefato de deploy do backend (container/imagem Java) e pipeline de build
- [ ] 13.2 Criar build estático do frontend e configurar hospedagem/CDN e domínio
- [ ] 13.3 Validar backend + frontend integrados em staging contra o dump de produção
- [ ] 13.4 Backup completo do PostgreSQL de produção antes da virada
- [ ] 13.5 Cutover: apontar DNS/proxy do site e o webhook da Evolution API para o novo backend
- [ ] 13.6 Validação pós-cutover (login, catálogo, envio, webhook recebendo mensagens reais, venda)
- [ ] 13.7 Congelar/arquivar o repositório Django mantendo-o reversível como rollback
