## ADDED Requirements

### Requirement: Gestão de carrinho
O backend SHALL manter um carrinho por conversa com status (`open`/`finalized`/`cancelled`), permitindo adicionar item, atualizar quantidade, remover item, ver e cancelar (limpar) o carrinho. Cada item SHALL registrar um snapshot do preço unitário no momento da adição e um produto não SHALL duplicar no mesmo carrinho.

#### Scenario: Adicionar item captura snapshot de preço
- **WHEN** um usuário adiciona um produto ao carrinho
- **THEN** o backend registra o item com `unit_price` igual ao preço atual do produto

#### Scenario: Produto já no carrinho
- **WHEN** um usuário adiciona um produto já presente no carrinho
- **THEN** o backend atualiza a quantidade do item existente em vez de criar duplicata

### Requirement: Checkout em transação atômica
O backend SHALL finalizar o carrinho em uma transação atômica: para cada item de produto com `stock_active=true` deduz `stock_quantity` de forma segura contra corrida (expressão atômica); se o estoque for insuficiente em qualquer item, SHALL reverter toda a transação. Ao concluir, SHALL criar a Venda com o total, criar os itens de venda com snapshot de nome e preço, e marcar o carrinho como `finalized`.

#### Scenario: Finalização bem-sucedida
- **WHEN** um usuário finaliza um carrinho com estoque suficiente
- **THEN** o backend deduz o estoque, cria a Venda e seus itens, e marca o carrinho como `finalized`

#### Scenario: Estoque insuficiente causa rollback
- **WHEN** um item do carrinho excede o estoque disponível na finalização
- **THEN** o backend reverte toda a transação e nenhuma dedução, venda ou finalização é persistida

### Requirement: Venda rápida
O backend SHALL permitir a venda direta de um único produto sem carrinho, aplicando a mesma dedução atômica de estoque e criando Venda e item de venda diretamente.

#### Scenario: Venda rápida com estoque
- **WHEN** um usuário realiza uma venda rápida de um produto com estoque suficiente
- **THEN** o backend deduz o estoque e cria a Venda com um item

### Requirement: Histórico imutável de vendas
O backend SHALL tratar a Venda como registro imutável, preservando o nome do produto (snapshot) mesmo que o produto seja posteriormente excluído.

#### Scenario: Produto excluído após a venda
- **WHEN** um produto vendido é excluído posteriormente
- **THEN** o item de venda mantém o `product_name` e o `unit_price` registrados na transação
