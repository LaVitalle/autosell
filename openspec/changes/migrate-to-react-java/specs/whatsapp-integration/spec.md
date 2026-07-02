## ADDED Requirements

### Requirement: Envio de mensagem de texto e mídia
O backend SHALL enviar mensagens de texto e de mídia (imagem/áudio/documento) via Evolution API, resolvendo o número do destinatário priorizando `phone` (JID) sobre `lid`/`remote_jid`.

#### Scenario: Envio de texto
- **WHEN** um usuário envia texto para um contato com telefone conhecido
- **THEN** o backend chama a Evolution API `sendText` para o número resolvido e registra a mensagem como enviada

#### Scenario: Resolução de número sem telefone
- **WHEN** o contato possui apenas `lid` sem `phone`
- **THEN** o backend usa o `lid`/`remote_jid` como destinatário

### Requirement: Envio de produto individual
O backend SHALL enviar um produto formatado como `*Nome*` + descrição + linha de estoque + preço; se o produto tiver imagem, SHALL enviar como mídia com legenda, caso contrário como texto.

#### Scenario: Produto com imagem
- **WHEN** um usuário envia um produto que possui imagem
- **THEN** o backend envia mídia com o texto formatado como legenda

#### Scenario: Produto sem imagem
- **WHEN** um usuário envia um produto sem imagem
- **THEN** o backend envia o texto formatado como mensagem de texto

### Requirement: Envio de categoria
O backend SHALL enviar todos os produtos de uma categoria individualmente e em sequência, excluindo produtos esgotados (`stock_active=true` e `stock_quantity=0`).

#### Scenario: Categoria com produtos disponíveis e esgotados
- **WHEN** um usuário envia uma categoria com produtos disponíveis e esgotados
- **THEN** o backend envia apenas os disponíveis, um a um

#### Scenario: Resultado parcial de envio
- **WHEN** parte dos envios de uma categoria falha
- **THEN** o backend retorna 207 (parcial); retorna 200 se todos tiverem sucesso e 500 se todos falharem

### Requirement: Envio de catálogo completo
O backend SHALL enviar o catálogo agrupando produtos por categoria com cabeçalhos, incluindo produtos sem categoria e excluindo esgotados, como uma única mensagem de texto.

#### Scenario: Catálogo agrupado
- **WHEN** um usuário solicita o envio do catálogo
- **THEN** o backend monta um texto único com cabeçalhos por categoria e a seção de produtos sem categoria, omitindo esgotados

### Requirement: Registro de envios em massa
O backend SHALL registrar cada envio em massa (fora do contexto de conversa) com tipo (`product` ou `category`) e status (`pending` → `sent`/`failed`).

#### Scenario: Envio em massa concluído
- **WHEN** um envio em massa de produto é concluído com sucesso
- **THEN** o registro correspondente tem status `sent`
