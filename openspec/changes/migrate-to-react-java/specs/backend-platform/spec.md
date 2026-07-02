## ADDED Requirements

### Requirement: Contrato de resposta JSON padronizado
O backend SHALL responder a todos os endpoints de API em JSON usando o envelope padrão contendo `data`, `status` (com `code` e `message`) e, quando aplicável, `page` (paginação) e `stats` (agregações).

#### Scenario: Resposta de listagem paginada
- **WHEN** um cliente autenticado faz GET em um endpoint de listagem
- **THEN** o backend retorna `data` como array, `status.code` igual a 200 e `page` com `current`, `per_page`, `total_items` e `total_pages`

#### Scenario: Limite máximo de paginação
- **WHEN** um cliente solicita `per_page` acima de 100
- **THEN** o backend limita a quantidade a no máximo 100 itens por página

### Requirement: Autenticação e proteção de endpoints
O backend SHALL exigir autenticação em todos os endpoints de API e páginas, exceto os webhooks da Evolution API. A sessão autenticada SHALL ser emitida via cookie HttpOnly consumível pelo frontend.

#### Scenario: Requisição não autenticada
- **WHEN** um cliente sem sessão válida acessa um endpoint protegido
- **THEN** o backend retorna 401/403 e não expõe dados

#### Scenario: Login bem-sucedido
- **WHEN** um usuário envia credenciais válidas ao endpoint de autenticação
- **THEN** o backend cria a sessão, retorna sucesso e o cookie de sessão HttpOnly

### Requirement: CORS entre frontend e backend
O backend SHALL permitir requisições cross-origin apenas dos domínios configurados do frontend, com suporte a credenciais (cookies).

#### Scenario: Origem permitida
- **WHEN** o frontend hospedado em um domínio autorizado faz uma requisição com credenciais
- **THEN** o backend responde com os cabeçalhos CORS apropriados permitindo a origem

#### Scenario: Origem não autorizada
- **WHEN** uma origem não listada faz uma requisição
- **THEN** o backend não inclui os cabeçalhos que autorizam a origem

### Requirement: Tratamento centralizado de erros e logging
O backend SHALL capturar exceções não tratadas de API, registrar um log estruturado (nível, origem, mensagem, trace, método, path, usuário) e retornar 500 com o envelope de resposta padrão, sem vazar stack trace ao cliente.

#### Scenario: Exceção em endpoint de API
- **WHEN** uma exceção não tratada ocorre durante o processamento de um endpoint
- **THEN** o backend grava um registro de log com nível ERROR e retorna `status.code` 500 com mensagem genérica

### Requirement: Configuração por variáveis de ambiente
O backend SHALL ler toda a configuração sensível (banco, Evolution API, MinIO, URL do site, secret) de variáveis de ambiente, sem valores secretos versionados.

#### Scenario: Inicialização sem variável obrigatória
- **WHEN** o backend inicia sem uma variável de ambiente obrigatória
- **THEN** a inicialização falha com mensagem clara indicando a variável ausente
