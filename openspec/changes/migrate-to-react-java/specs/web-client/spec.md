## ADDED Requirements

### Requirement: SPA consumindo o backend via API
O frontend SHALL ser uma Single Page Application em React que renderiza todas as telas (dashboard, produtos, categorias, contatos, mensagens, live chat) consumindo exclusivamente a API JSON do backend, sem renderização de templates no servidor.

#### Scenario: Navegação sem recarga de página
- **WHEN** um usuário navega entre as seções do painel
- **THEN** o frontend troca de rota no cliente e carrega os dados via chamadas de API, sem recarregar a página inteira

### Requirement: Fluxo de autenticação no cliente
O frontend SHALL fornecer uma tela de login que autentica contra o backend, manter a sessão via cookie HttpOnly enviado nas requisições e redirecionar usuários não autenticados para o login.

#### Scenario: Acesso sem sessão
- **WHEN** um usuário não autenticado acessa uma rota protegida do frontend
- **THEN** o frontend redireciona para a tela de login

#### Scenario: Logout
- **WHEN** um usuário realiza logout
- **THEN** o frontend encerra a sessão no backend e retorna à tela de login

### Requirement: Padrões de loading UX
O frontend SHALL aplicar os padrões de carregamento: skeleton shimmer nos stat cards, placeholder de loading nos containers, fade-in do conteúdo após resposta da API e números animados nos stat cards, sem gerar linhas de skeleton falsas.

#### Scenario: Carregamento de uma listagem
- **WHEN** uma tela de listagem inicia a busca de dados
- **THEN** o frontend exibe o placeholder de loading e, ao receber a resposta, aplica fade-in e anima os contadores

### Requirement: Dark mode persistente
O frontend SHALL oferecer dark mode baseado em classe, persistido em `localStorage`, com prevenção de FOUC na carga inicial e alternância por controle na interface.

#### Scenario: Preferência persistida
- **WHEN** um usuário ativa o dark mode e recarrega a aplicação
- **THEN** o frontend inicia já em dark mode sem flash de tema claro

### Requirement: Layout responsivo e zero-scroll
O frontend SHALL seguir o design system (mobile-first, política de zero scroll vertical, truncamento/tooltip de textos longos) reproduzindo a experiência visual atual em todos os breakpoints.

#### Scenario: Texto longo em card
- **WHEN** um título ou descrição excede o espaço disponível
- **THEN** o frontend trunca o texto e expõe o conteúdo completo via atributo de título/tooltip, sem quebrar o layout
