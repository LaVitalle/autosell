## ADDED Requirements

### Requirement: CRUD de produtos
O backend SHALL permitir criar, listar (paginado, com busca e estatísticas), editar e excluir produtos. O nome SHALL ter entre 4 e 90 caracteres e o preço SHALL ser maior que zero.

#### Scenario: Criar produto válido
- **WHEN** um usuário envia nome (4-90 chars), preço > 0 e demais campos válidos
- **THEN** o backend persiste o produto e retorna 200 com os dados do produto

#### Scenario: Rejeitar preço inválido
- **WHEN** um usuário envia preço menor ou igual a zero
- **THEN** o backend retorna erro de validação de campo e não persiste

#### Scenario: Listagem com busca e estatísticas
- **WHEN** um usuário lista produtos com termo de busca
- **THEN** o backend retorna os produtos correspondentes paginados junto com `stats`

### Requirement: Regras de estoque de produto
O backend SHALL aplicar as regras de estoque: com `stock_active=false` o produto é de produção contínua (sempre disponível); com `stock_active=true` a disponibilidade é controlada por `stock_quantity`; com `stock_active=true` e `stock_quantity=0` o produto está esgotado. Ao definir `stock_active=false`, `stock_quantity` SHALL ser redefinido para 0.

#### Scenario: Produto contínuo sempre disponível
- **WHEN** um produto tem `stock_active=false`
- **THEN** o produto é tratado como sempre disponível independentemente de `stock_quantity`

#### Scenario: Produto esgotado
- **WHEN** um produto tem `stock_active=true` e `stock_quantity=0`
- **THEN** o produto é classificado como esgotado

#### Scenario: Desativar controle de estoque zera quantidade
- **WHEN** um usuário altera um produto para `stock_active=false`
- **THEN** o backend define `stock_quantity` como 0

### Requirement: CRUD de categorias com relacionamento M2M
O backend SHALL permitir criar, listar (com contagem de produtos), editar e excluir categorias, e remover um produto de uma categoria. Uma categoria SHALL relacionar-se a múltiplos produtos e um produto a múltiplas categorias.

#### Scenario: Listagem com contagem de produtos
- **WHEN** um usuário lista categorias
- **THEN** cada categoria retorna a quantidade de produtos associados

#### Scenario: Remover produto da categoria
- **WHEN** um usuário remove um produto específico de uma categoria
- **THEN** a associação é desfeita sem excluir o produto nem a categoria

### Requirement: Upload de imagem de produto e categoria
O backend SHALL aceitar upload de imagem para produtos e categorias, armazenando no MinIO com nome sanitizado sob os caminhos `products/{uuid}.ext` e `categories/{uuid}.ext`, e persistir a URL resultante.

#### Scenario: Upload com extensão permitida
- **WHEN** um usuário envia uma imagem com extensão permitida
- **THEN** o backend armazena o arquivo no MinIO e salva a URL no registro

#### Scenario: Extensão não permitida
- **WHEN** um usuário envia um arquivo com extensão fora da lista permitida
- **THEN** o backend rejeita o upload com erro de validação
