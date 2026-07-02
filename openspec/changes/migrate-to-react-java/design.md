## Context

O AutoSell é um monólito Django 5.2.5 (Python 3.13) que serve HTML (templates + Tailwind CDN + Vanilla JS) e API JSON no mesmo processo, com PostgreSQL em produção, MinIO para storage e integração com a Evolution API (WhatsApp) via HTTP e webhook. O objetivo é dividir em dois repositórios independentes — **frontend React** e **backend Java** — preservando 100% do comportamento funcional (catálogo, contatos, WhatsApp, live chat, carrinho/vendas) e reaproveitando o banco PostgreSQL existente.

Restrições relevantes: o contrato de API atual (`data`/`status`/`page`/`stats`), a semântica LID/JID da Evolution API, as regras de estoque (`stock_active`), a normalização de telefone, a transação atômica de venda e o design system (dark mode, zero-scroll, loading UX) devem ser reproduzidos fielmente. Não há testes automatizados nem CI/CD hoje.

## Goals / Non-Goals

**Goals:**
- Backend Java (Spring Boot) em repositório próprio expondo a mesma API JSON, com paridade de contrato rota-a-rota.
- Frontend React (SPA) em repositório próprio consumindo apenas a API.
- Reuso do banco PostgreSQL de produção via mapeamento JPA 1:1 (mesmas tabelas/colunas/índices), sem migração destrutiva de dados.
- Paridade comportamental do webhook (eco, merge LID/JID, status), integrações Evolution/MinIO e regras de negócio.
- Estratégia de virada (cutover) com rollback viável para o Django atual.

**Non-Goals:**
- Alterar requisitos funcionais ou regras de negócio.
- Trocar o provedor de WhatsApp, o banco de produção ou o MinIO.
- Introduzir microserviços — o backend Java é um único serviço (monólito modular).
- Migrar de polling para WebSocket nesta fase (mantém-se o polling).
- Redesenhar a UI — a UX atual é reproduzida, não repensada.

## Decisions

### D1 — Backend: Spring Boot 3.x + Java 21 (LTS)
Adotar Spring Boot 3.x (Spring Web MVC, Spring Data JPA/Hibernate, Spring Security) sobre Java 21 LTS, build com Maven. Estrutura em pacotes por domínio (`catalog`, `contact`, `whatsapp`, `livechat`, `sales`, `platform`) espelhando os apps Django.
- **Por quê**: ecossistema maduro, JPA cobre o ORM 1:1 com o schema existente, Spring Security cobre sessão/CORS, integração HTTP simples. Alternativas consideradas: Quarkus/Micronaut (menor comunidade/menos familiaridade), Java EE puro (mais boilerplate).

### D2 — Persistência: JPA/Hibernate mapeando o schema existente, sem gerar DDL
Configurar `hibernate.ddl-auto=validate` (nunca `update`/`create`) e mapear entidades para as tabelas Django já existentes (`products_product`, `livechat_conversation`, etc.), incluindo o snapshot de preço/nome e os índices. Usar `@Version`/bloqueio pessimista ou `UPDATE ... SET qty = qty - :n WHERE qty >= :n` para a dedução atômica de estoque (equivalente ao `F()`/`select_for_update`).
- **Por quê**: preserva os dados de produção sem migração de esquema. Alternativa (novo schema + ETL) foi descartada por risco e custo. Migrations futuras via Flyway/Liquibase (fora do escopo inicial, apenas baseline).

### D3 — Autenticação: sessão server-side com cookie HttpOnly + CSRF para mutações
Manter o modelo de sessão (equivalente ao Django), com Spring Security emitindo cookie de sessão HttpOnly; o frontend envia credenciais com `withCredentials`. CSRF via token para requisições mutantes do frontend; webhooks permanecem isentos e protegidos por IP.
- **Por quê**: menor divergência do modelo atual e mais seguro para SPA de painel (cookie HttpOnly evita exposição de token a XSS). Alternativa JWT em `localStorage` foi descartada por superfície de XSS e por exigir gestão de refresh. O hash de senha do Django (`pbkdf2_sha256`) será reconhecido por um `PasswordEncoder` compatível para não invalidar logins existentes.

### D4 — Frontend: React + Vite + TypeScript + Tailwind + React Router + TanStack Query
SPA com Vite (build estático), TypeScript, Tailwind (config `darkMode: 'class'` reproduzindo o design system), React Router para navegação e TanStack Query para data-fetching/cache e o polling do live chat.
- **Por quê**: Vite dá build rápido e artefato estático simples de hospedar; TanStack Query modela naturalmente o polling `since=<ISO>` e o cache de listagens. Alternativa Next.js foi descartada (SSR desnecessário para um painel autenticado).

### D5 — Contrato de API preservado + camada anticorrupção nas integrações
Reimplementar cada rota com método, path e envelope idênticos. Encapsular Evolution API e MinIO em clientes dedicados (`EvolutionClient`, `StorageService`) que reproduzem `evoapi.py`/`storage.py`, incluindo resolução de número (phone > lid), formatação de produto/catálogo e caminhos de storage (`products/`, `categories/`, `chat_media/`).
- **Por quê**: mantém o webhook e integrações desacoplados do domínio e facilita testar paridade. Cliente HTTP: `RestClient`/`WebClient` do Spring.

### D6 — Webhook com paridade estrita
Porta 1:1 de `livechat/webhook.py`: whitelist de IP, isenção de CSRF, `messages.upsert`/`messages.update`, prioridade de download de mídia (getBase64 → base64 → mediaUrl → jpegThumbnail), janela de 30s para eco e algoritmo de merge (menor ID primário).
- **Por quê**: é a área de maior risco de regressão; deve ser reproduzida linha-a-linha em semântica e coberta por testes.

## Risks / Trade-offs

- **[Divergência de contrato de API quebra o frontend]** → Congelar o contrato a partir do CLAUDE.md/rotas atuais; criar testes de contrato (mesmos payloads de entrada/saída) comparando respostas Django vs Java antes do cutover.
- **[Comportamento do webhook (LID/JID, eco, merge) diverge]** → Porta guiada por testes com payloads reais capturados da Evolution API; validar merge e eco em ambiente de staging antes de apontar o webhook para o novo backend.
- **[Hashes de senha do Django incompatíveis com Spring Security]** → Implementar `PasswordEncoder` que valida `pbkdf2_sha256` do Django (ou forçar reset de senha na virada como fallback).
- **[Dedução de estoque sem atomicidade real]** → Usar UPDATE condicional atômico + transação; testar concorrência (duas finalizações simultâneas do mesmo estoque).
- **[Perda de dados na reutilização do PostgreSQL]** → `ddl-auto=validate`, backup completo antes do cutover, ambiente de staging com dump de produção.
- **[Paridade de UX/regras de estoque no frontend]** → Reproduzir badges (Contínuo/X unidades/Esgotado), zero-scroll e loading UX; revisão visual contra o app atual.
- **[Trade-off: dois deploys e CORS entre domínios]** → Configurar CORS com credenciais para o domínio do frontend; documentar variáveis de ambiente por repositório.

## Migration Plan

1. **Baseline de dados**: documentar o schema atual (introspecção do PostgreSQL) e criar dump de produção para staging.
2. **Backend Java (staging)**: montar Spring Boot, mapear entidades JPA com `validate`, implementar domínio por domínio (platform → catalog → contact → whatsapp → livechat → sales), validando o envelope de resposta.
3. **Testes de contrato**: rodar Django e Java lado a lado contra o mesmo banco de staging, comparando respostas das rotas e o comportamento do webhook (payloads reais).
4. **Frontend React (staging)**: implementar a SPA consumindo o backend Java em staging, reproduzindo telas, auth e design system.
5. **Cutover**: com backend e frontend validados, apontar DNS/proxy do site e do webhook da Evolution API para o novo backend; congelar o repositório Django.
6. **Rollback**: manter o Django atual implantável e o webhook reversível; como o banco é compartilhado e mapeado 1:1, reverter DNS/webhook restaura o sistema anterior sem migração de dados.

## Open Questions

- Confirmar Maven vs Gradle e Java 21 vs 17 como versões definitivas do backend.
- Confirmar reuso dos hashes de senha do Django vs reset de senhas na virada.
- Confirmar host de deploy do frontend estático (mesmo Easypanel/CDN) e domínio (subdomínio vs path).
- Definir se o polling permanece igual ou recebe pequenos ajustes de intervalo no novo cliente.
