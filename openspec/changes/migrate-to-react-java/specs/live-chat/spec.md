## ADDED Requirements

### Requirement: Gestão de conversas e mensagens
O backend SHALL manter conversas (uma por contato) e mensagens de chat, expondo endpoints para listar conversas, ler mensagens de uma conversa, enviar texto/produto/categoria/catálogo, marcar como lida, atualizar o contato, iniciar e excluir conversa.

#### Scenario: Enviar texto em conversa
- **WHEN** um usuário envia texto em uma conversa
- **THEN** o backend envia via WhatsApp, persiste a mensagem com direção `out` e atualiza `last_message_text`, `last_message_at` e `last_message_direction`

#### Scenario: Marcar conversa como lida
- **WHEN** um usuário marca uma conversa como lida
- **THEN** o backend zera `unread_count` e sinaliza a leitura ao WhatsApp

### Requirement: Ingestão de mensagens recebidas via webhook
O backend SHALL aceitar o webhook da Evolution API validado por whitelist de IP, sem CSRF, processando os eventos `messages.upsert` e `messages.update`. Para mensagens recebidas, SHALL extrair texto/mídia, resolver o contato por `lid` e `phone`, baixar mídia para o MinIO e criar/atualizar a conversa e a mensagem.

#### Scenario: IP não autorizado
- **WHEN** uma requisição de webhook chega de um IP fora da whitelist
- **THEN** o backend rejeita a requisição sem processá-la

#### Scenario: Mensagem recebida com mídia
- **WHEN** chega um `messages.upsert` com mídia (fromMe=false)
- **THEN** o backend baixa a mídia para o MinIO, cria a mensagem com direção `in` e incrementa `unread_count`

### Requirement: Detecção de eco de mensagens enviadas
O backend SHALL, ao receber um `messages.upsert` com fromMe=true cujo conteúdo corresponda a uma mensagem `pending` dos últimos 30 segundos, atualizar o `wpp_message_id` da mensagem original em vez de criar uma duplicata.

#### Scenario: Eco de mensagem enviada pelo painel
- **WHEN** chega um evento fromMe=true correspondente a uma mensagem `pending` recente
- **THEN** o backend atualiza o `wpp_message_id` da mensagem existente e não cria duplicata

### Requirement: Merge de contatos LID/JID
O backend SHALL, quando `lid` e `phone` de uma mensagem apontarem para contatos diferentes, mesclar os contatos mantendo o de menor ID como primário, movendo mensagens, carrinhos e vendas do secundário, enriquecendo o primário e excluindo o secundário.

#### Scenario: Conflito de identidade
- **WHEN** uma mensagem recebida identifica que `lid` e `phone` pertencem a contatos distintos
- **THEN** o backend consolida tudo no contato de menor ID e remove o secundário

### Requirement: Atualização de status de mensagem
O backend SHALL atualizar o status das mensagens a partir de `messages.update` mapeando códigos 2→sent, 3→delivered, 4→read, 5→read, e aceitando as strings equivalentes; o status SHALL apenas avançar, nunca retroceder.

#### Scenario: Avanço de status
- **WHEN** chega um update com código 4 (read) para uma mensagem `delivered`
- **THEN** o backend atualiza o status para `read`

#### Scenario: Status não retrocede
- **WHEN** chega um update com código inferior ao status atual da mensagem
- **THEN** o backend mantém o status atual

### Requirement: Atualizações por polling
O backend SHALL expor um endpoint de polling que retorna as atualizações desde um timestamp informado (`since` em ISO), permitindo ao frontend refletir novas mensagens e mudanças de status sem WebSocket.

#### Scenario: Polling com timestamp
- **WHEN** o frontend consulta o polling com um `since`
- **THEN** o backend retorna as conversas e mensagens alteradas após esse instante
