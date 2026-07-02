## ADDED Requirements

### Requirement: CRUD de contatos
O backend SHALL permitir criar, listar (com contagem de mensagens), editar e excluir contatos. O nome SHALL ter entre 3 e 60 caracteres. `lid` e `phone` SHALL ser únicos.

#### Scenario: Criar contato válido
- **WHEN** um usuário envia nome (3-60 chars) e telefone válido
- **THEN** o backend persiste o contato e retorna 200

#### Scenario: Telefone duplicado
- **WHEN** um usuário cria um contato com telefone já existente
- **THEN** o backend retorna erro de unicidade e não persiste

#### Scenario: Listagem com contagem de mensagens
- **WHEN** um usuário lista contatos
- **THEN** cada contato retorna a quantidade de mensagens associadas

### Requirement: Normalização de telefone
O backend SHALL normalizar telefones removendo os caracteres `(`, `)`, `-`, espaço e `+`; quando o resultado tiver 11 dígitos, SHALL prefixar `55`; o formato final SHALL ter 13 dígitos no padrão `55XXXXXXXXXXX`.

#### Scenario: Telefone com máscara e 11 dígitos
- **WHEN** um usuário informa um telefone com máscara e 11 dígitos após limpeza
- **THEN** o backend armazena o telefone como `55` seguido dos 11 dígitos

#### Scenario: Telefone já com código do país
- **WHEN** um usuário informa um telefone que já tem 13 dígitos com prefixo 55
- **THEN** o backend mantém o formato `55XXXXXXXXXXX`

### Requirement: Identidade LID e JID do WhatsApp
O backend SHALL persistir `lid` (identificador do WhatsApp derivado do `remoteJid`) e `phone` (JID real) como campos distintos e indexados, permitindo que um contato exista inicialmente apenas com `lid`.

#### Scenario: Contato criado apenas com LID
- **WHEN** uma mensagem originada pelo próprio número (fromMe=true) cria um contato sem telefone conhecido
- **THEN** o backend cria o contato apenas com `lid`, deixando `phone` vazio até uma mensagem recebida populá-lo
