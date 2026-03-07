# 🎨 AutoSell - Guia Completo de Estilo e Design System

## 📋 Visão Geral

Este documento consolida e detalha completamente o sistema de design do **AutoSell**, uma plataforma de gestão de produtos com foco em design minimalista, usabilidade e experiência do usuário moderna. A marca se destaca pela simplicidade visual, paleta de cores neutras e funcionalidade intuitiva **sem necessidade de scroll vertical**.

---

## 🎯 Princípios Fundamentais de Design

### Filosofia da Marca
- **Minimalismo Funcional**: Interface limpa onde cada elemento tem um propósito específico
- **Zero Scroll Policy**: Telas devem ocupar 100% da viewport sem necessidade de scroll vertical
- **Mobile-First**: Design responsivo pensado primeiro para dispositivos móveis
- **Usabilidade Máxima**: Foco na experiência do usuário e facilidade de uso
- **Consistência Total**: Padrões uniformes em todo o sistema
- **Profissionalismo Moderno**: Aparência contemporânea e confiável
- **Acessibilidade Universal**: Design inclusivo e legível para todos

### Valores Visuais Essenciais
- **Simplicidade**: Cada elemento tem um propósito claro e definido
- **Elegância**: Estética refinada e contemporânea
- **Clareza**: Comunicação visual direta e objetiva
- **Responsividade Inteligente**: Adaptação perfeita a todos os dispositivos
- **Performance**: Transições suaves e carregamento rápido

---

## 🎨 Sistema de Cores Unificado

### Paleta Principal (Neutral Scale)
```css
/* Escala Neutral Completa - Base do Sistema */
neutral-50:  #fafafa    /* Fundo principal - modo claro */
neutral-100: #f5f5f5   /* Fundos secundários e hover states */
neutral-200: #e5e5e5   /* Bordas e divisores principais */
neutral-300: #d4d4d4   /* Bordas sutis e inputs */
neutral-400: #a3a3a3   /* Textos secundários e placeholders */
neutral-500: #737373   /* Textos médios e ícones */
neutral-600: #525252   /* Textos importantes */
neutral-700: #404040   /* Fundos escuros e sidebar */
neutral-800: #262626   /* Cards e componentes dark mode */
neutral-900: #171717   /* Fundo principal - modo escuro */
neutral-950: #0a0a0a   /* Fundos muito escuros (reserva) */
```

### Cores de Estado e Feedback
```css
/* Estados de Sucesso */
green-100: #dcfce7     /* Fundo de badges ativas */
green-500: #22c55e     /* Texto de badges ativas */
green-600: #16a34a     /* Hover de elementos verdes */
green-800: #166534     /* Texto green dark mode */
green-900: #14532d     /* Fundo green dark mode */

/* Estados de Erro/Perigo */
red-100: #fee2e2       /* Fundo de mensagens de erro */
red-300: #fca5a5       /* Bordas de inputs com erro */
red-400: #f87171       /* Texto de mensagens de erro */
red-500: #ef4444       /* Botões de ação destrutiva */
red-600: #dc2626       /* Hover de botões destrutivos */
red-700: #b91c1c       /* Estados ativos destrutivos */
red-800: #991b1b       /* Bordas red dark mode */
red-900: #7f1d1d       /* Fundos red dark mode */

/* Estados Informativos */
blue-100: #dbeafe      /* Fundo de badges informativos */
blue-500: #3b82f6      /* Texto de badges informativos */
blue-600: #2563eb      /* Hover de elementos azuis */
blue-800: #1e40af      /* Texto blue dark mode */
blue-900: #1e3a8a      /* Fundo blue dark mode */
```

### Modo Claro vs Modo Escuro
```css
/* Modo Claro (Padrão) */
body-light: bg-neutral-50, text-neutral-900
cards-light: bg-white, border-neutral-200
hover-light: hover:bg-neutral-100

/* Modo Escuro */
body-dark: bg-neutral-900, text-neutral-50
cards-dark: bg-neutral-800, border-neutral-700
hover-dark: hover:bg-neutral-700

/* Transições entre Modos */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)
```

---

## 🔤 Sistema Tipográfico Completo

### Hierarquia de Textos Definida
```css
/* Títulos Principais */
h1-page: text-2xl md:text-3xl font-bold     /* Títulos principais de página */
h1-compact: text-xl md:text-2xl font-bold   /* Títulos em layouts compactos */
h2-section: text-lg font-semibold           /* Subtítulos de seção */
h3-card: text-base font-semibold            /* Títulos de cards */

/* Navegação e Interface */
nav-primary: text-sm font-medium            /* Itens de menu principal */
nav-secondary: text-xs font-medium          /* Itens de submenu */
button-text: text-sm font-medium            /* Texto de botões */
button-small: text-xs font-medium           /* Botões pequenos/mobile */

/* Conteúdo e Dados */
body-primary: text-sm                       /* Texto padrão */
body-secondary: text-xs                     /* Texto secundário */
caption: text-xs                            /* Legendas e metadados */
stats-large: text-lg font-bold             /* Números grandes (compacto) */
stats-big: text-xl md:text-2xl font-bold   /* Números de estatísticas */

/* Labels e Formulários */
label-text: text-sm font-medium             /* Labels de formulários */
input-text: text-sm                         /* Texto de inputs */
error-text: text-sm                         /* Mensagens de erro */
help-text: text-xs                          /* Textos de ajuda */
```

### Configuração de Fontes
```css
/* Família de Fontes */
font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif

/* Pesos Utilizados */
font-medium: 500    /* Para navegação e labels */
font-semibold: 600  /* Para subtítulos */
font-bold: 700      /* Para títulos e números */

/* Altura de Linha */
leading-normal: 1.5     /* Texto padrão */
leading-relaxed: 1.625  /* Texto de leitura */
leading-tight: 1.25     /* Títulos */
```

---

## 🧩 Componentes do Sistema Atualizado

### 1. Layout Principal - Zero Scroll
```css
/* Container Raiz */
.main-container {
    max-width: max-w-7xl;
    margin: 0 auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: mobile-content-padding;
}

/* Distribuição de Altura */
.header-section { margin-bottom: mb-4; }      /* Header compacto */
.stats-section { margin-bottom: mb-4; }       /* Cards de estatísticas */
.content-section { flex: 1; overflow: hidden; } /* Conteúdo principal */
```

### 2. Header Compacto
```css
/* Container do Header */
.header-compact {
    display: flex;
    flex-direction: column sm:flex-row;
    align-items: start sm:center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}

/* Título com Ícone */
.title-section {
    display: flex;
    align-items: center;
    space-x: 0.75rem;
}

.title-icon {
    width: 2rem;
    height: 2rem;
    background: bg-neutral-100 dark:bg-neutral-700;
    border-radius: rounded-lg;
    display: flex;
    align-items: center;
    justify-content: center;
}

.title-text {
    font-size: text-xl md:text-2xl;
    font-weight: font-bold;
    color: text-neutral-900 dark:text-white;
}

.subtitle-text {
    font-size: text-xs md:text-sm;
    color: text-neutral-600 dark:text-neutral-400;
}
```

### 3. Área de Busca e Ações Integrada
```css
/* Container de Ações */
.actions-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

/* Campo de Busca */
.search-container {
    position: relative;
    flex: 1 sm:flex-none;
}

.search-input {
    width: w-full sm:w-64;
    padding: px-3 py-2;
    font-size: text-sm;
    border: border-neutral-300 dark:border-neutral-600;
    border-radius: rounded-lg;
    background: bg-white dark:bg-neutral-700;
    color: text-neutral-900 dark:text-white;
    placeholder: placeholder-neutral-500 dark:placeholder-neutral-400;
    focus: focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400;
    transition: transition-colors duration-200;
}

.search-icon {
    position: absolute;
    right: 0.75rem;
    top: 0.625rem;
    width: 1rem;
    height: 1rem;
    color: text-neutral-400;
}
```

### 4. Cards de Estatísticas Compactos
```css
/* Grid de Cards */
.stats-grid {
    display: grid;
    grid-template-columns: grid-cols-2 lg:grid-cols-4;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

/* Card Individual */
.stats-card {
    background: bg-white dark:bg-neutral-800;
    padding: 0.75rem;
    border-radius: rounded-lg;
    border: border-neutral-200 dark:border-neutral-700;
    box-shadow: shadow-sm;
}

.stats-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.stats-text {
    font-size: text-xs;
    font-weight: font-medium;
    color: text-neutral-600 dark:text-neutral-400;
}

.stats-number {
    font-size: text-lg;
    font-weight: font-bold;
    color: text-neutral-900 dark:text-white;
}

.stats-icon {
    width: 2rem;
    height: 2rem;
    background: bg-neutral-100 dark:bg-neutral-700;
    border-radius: rounded-lg;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

### 5. Tabelas Responsivas com Altura Fixa
```css
/* Container de Conteúdo Principal */
.content-container {
    background: bg-white dark:bg-neutral-800;
    border-radius: rounded-xl;
    border: border-neutral-200 dark:border-neutral-700;
    box-shadow: shadow-sm;
    overflow: hidden;
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* Header da Tabela */
.table-header {
    padding: px-4 md:px-6 py-3;
    border-bottom: border-b border-neutral-200 dark:border-neutral-700;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Área de Conteúdo com Scroll */
.table-content {
    flex: 1;
    overflow: hidden;
}

/* Versão Desktop */
.desktop-table {
    display: hidden md:block;
    height: 100%;
    overflow-y: auto;
}

.table-head {
    background: bg-neutral-50 dark:bg-neutral-700;
    position: sticky;
    top: 0;
}

.table-header-cell {
    padding: px-4 py-3;
    text-align: left;
    font-size: text-xs;
    font-weight: font-medium;
    color: text-neutral-700 dark:text-neutral-300;
    text-transform: uppercase;
    letter-spacing: tracking-wider;
}

/* Versão Mobile */
.mobile-cards {
    display: block md:hidden;
    height: 100%;
    overflow-y: auto;
}
```

### 6. Sistema de Paginação JavaScript
```css
/* Container de Paginação */
.pagination-container {
    padding: px-4 md:px-6 py-3;
    border-top: border-t border-neutral-200 dark:border-neutral-700;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Controles de Itens por Página */
.items-per-page {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.items-select {
    font-size: text-sm;
    border: border-neutral-300 dark:border-neutral-600;
    border-radius: rounded;
    padding: px-2 py-1;
    background: bg-white dark:bg-neutral-700;
    color: text-neutral-900 dark:text-white;
    focus: focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400;
}

/* Navegação de Páginas */
.pagination-nav {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pagination-button {
    display: inline-flex;
    align-items: center;
    padding: px-3 py-1.5;
    border: border-neutral-300 dark:border-neutral-600;
    font-size: text-sm;
    font-weight: font-medium;
    border-radius: rounded;
    color: text-neutral-700 dark:text-neutral-300;
    background: bg-white dark:bg-neutral-800;
    hover: hover:bg-neutral-50 dark:hover:bg-neutral-700;
    transition: transition-colors duration-200;
    disabled: disabled:opacity-50 disabled:cursor-not-allowed;
}

.pagination-button-active {
    background: bg-neutral-900 dark:bg-white;
    color: text-white dark:text-neutral-900;
}
```

### 7. Botões do Sistema
```css
/* Botão Primário */
.btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: px-4 py-2;
    background: bg-neutral-900 dark:bg-white;
    color: text-white dark:text-neutral-900;
    font-weight: font-medium;
    border-radius: rounded-lg;
    hover: hover:bg-neutral-800 dark:hover:bg-neutral-100;
    transition: transition-all duration-200;
    box-shadow: shadow-sm hover:shadow-md;
    font-size: text-sm;
}

/* Botão Secundário */
.btn-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: px-3 py-1.5;
    border: border-neutral-300 dark:border-neutral-600;
    color: text-neutral-700 dark:text-neutral-300;
    font-weight: font-medium;
    border-radius: rounded;
    background: bg-white dark:bg-neutral-800;
    hover: hover:bg-neutral-50 dark:hover:bg-neutral-700;
    transition: transition-colors duration-200;
    font-size: text-xs;
}

/* Botão Destrutivo */
.btn-destructive {
    border: border-red-300 dark:border-red-600;
    color: text-red-700 dark:text-red-400;
    hover: hover:bg-red-50 dark:hover:bg-red-900/20;
}

/* Tamanhos de Botões */
.btn-small { padding: px-2 py-1; font-size: text-xs; }
.btn-medium { padding: px-3 py-1.5; font-size: text-xs; }
.btn-large { padding: px-4 py-2; font-size: text-sm; }
```

### 8. Formulários Responsivos
```css
/* Label */
.form-label {
    font-size: text-sm;
    font-weight: font-medium;
    color: text-neutral-700 dark:text-neutral-300;
    margin-bottom: 0.5rem;
    display: block;
}

/* Input Base */
.form-input {
    width: 100%;
    padding: px-4 py-3;
    border-radius: rounded-lg;
    border: border-neutral-300 dark:border-neutral-600;
    background: bg-white dark:bg-neutral-700;
    color: text-neutral-900 dark:text-white;
    placeholder: placeholder-neutral-500 dark:placeholder-neutral-400;
    focus: focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400;
    transition: transition-colors duration-200;
}

/* Textarea */
.form-textarea {
    resize: none;
    rows: 4;
}

/* File Input */
.form-file {
    file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0;
    file:text-sm file:font-medium file:bg-neutral-100 dark:file:bg-neutral-600;
    file:text-neutral-700 dark:file:text-neutral-300;
    hover:file:bg-neutral-200 dark:hover:file:bg-neutral-500;
}

/* Estados de Erro */
.form-input-error {
    border: border-red-300 dark:border-red-600;
    focus: focus:ring-red-500 dark:focus:ring-red-400;
}

.form-error-message {
    color: text-red-600 dark:text-red-400;
    font-size: text-sm;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
}
```

---

## 📐 Sistema de Espaçamento Zero-Scroll

### Base Matemática: 4px (0.25rem)
```css
/* Espaçamentos Internos */
p-1: 0.25rem (4px)      /* Micro espaçamentos */
p-2: 0.5rem (8px)       /* Espaçamentos pequenos */
p-3: 0.75rem (12px)     /* Padrão para cards compactos */
p-4: 1rem (16px)        /* Espaçamentos médios */
p-6: 1.5rem (24px)      /* Espaçamentos grandes */

/* Margens Verticais */
mb-2: 0.5rem (8px)      /* Separação mínima */
mb-3: 0.75rem (12px)    /* Separação pequena */
mb-4: 1rem (16px)       /* Separação padrão */
mb-6: 1.5rem (24px)     /* Separação grande */

/* Gaps de Grid */
gap-1: 0.25rem (4px)    /* Gaps mínimos */
gap-2: 0.5rem (8px)     /* Gaps pequenos */
gap-3: 0.75rem (12px)   /* Gaps padrão */
gap-4: 1rem (16px)      /* Gaps médios */

/* Espaçamentos Horizontais */
space-x-2: 0.5rem (8px)
space-x-3: 0.75rem (12px)
space-y-3: 0.75rem (12px)
space-y-4: 1rem (16px)
```

### Layout de Altura Fixa
```css
/* Estrutura Principal */
.layout-container {
    height: 100vh;               /* Altura total da viewport */
    display: flex;
    flex-direction: column;
}

/* Distribuição Vertical */
.header-compact { height: auto; margin-bottom: 1rem; }
.stats-compact { height: auto; margin-bottom: 1rem; }
.content-main { flex: 1; min-height: 0; }
.pagination-footer { height: auto; }

/* Responsividade Móvel */
@media (max-width: 768px) {
    .mobile-content-padding { padding: 0.75rem; }
    .stats-grid { gap: 0.75rem; }
    .stats-card { padding: 0.75rem; }
}
```

---

## 📱 Especificações Mobile-First

### Breakpoints Estratégicos
```css
/* Mobile First - Padrão */
default: < 640px          /* Smartphones */
sm: >= 640px             /* Smartphones grandes */
md: >= 768px             /* Tablets */
lg: >= 1024px            /* Desktops */
xl: >= 1280px            /* Telas grandes */
```

### Adaptações Mobile Específicas
```css
/* Header Mobile */
.mobile-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
}

.mobile-title {
    font-size: text-lg;      /* Menor que desktop */
    margin-bottom: 0.25rem;
}

.mobile-subtitle {
    font-size: text-xs;      /* Texto menor */
}

/* Busca Mobile */
.mobile-search {
    width: 100%;             /* Largura total */
    margin-bottom: 0.5rem;
}

/* Cards Mobile */
.mobile-stats {
    grid-template-columns: repeat(2, 1fr);  /* 2 colunas */
    gap: 0.75rem;
}

.mobile-card {
    padding: 0.75rem;        /* Padding reduzido */
}

/* Botões Mobile */
.mobile-button {
    padding: px-3 py-2;
    font-size: text-sm;
    width: 100% sm:auto;     /* Largura total no mobile */
}

.mobile-button-small {
    padding: px-2 py-1;
    font-size: text-xs;
}

/* Paginação Mobile */
.mobile-pagination {
    flex-direction: column sm:flex-row;
    gap: 0.75rem;
    align-items: stretch sm:center;
}

.mobile-pagination-controls {
    justify-content: center;
}
```

### Navigation Mobile
```css
/* Menu Mobile - Sidebar */
.mobile-menu-button {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 50;
    display: block md:hidden;
    padding: 0.5rem;
    background: bg-white dark:bg-neutral-800;
    border: border-neutral-200 dark:border-neutral-700;
    border-radius: rounded-lg;
    box-shadow: shadow-lg;
}

.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 16rem;
    background: bg-white dark:bg-neutral-800;
    border-right: border-neutral-200 dark:border-neutral-700;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 40;
}

.mobile-sidebar-open {
    transform: translateX(0);
}

.mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 30;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

.mobile-overlay-visible {
    opacity: 1;
}
```

---

## 📱 Responsividade e Text Overflow

### Sistema de Ellipsis para Textos Longos

**PADRÃO OBRIGATÓRIO**: Todos os elementos que podem receber textos longos devem implementar text overflow ellipsis com tooltips para manter a responsividade e evitar quebra de layout.

#### Princípios Fundamentais
1. **Prevenção de Layout Quebrado**: Textos nunca devem quebrar o design
2. **Tooltip Obrigatório**: Sempre adicionar `title` attribute com texto completo
3. **Controle de Largura**: Definir larguras máximas para containers de texto
4. **Flexbox Responsivo**: Usar `min-w-0` e `flex-1` para controle de overflow

### Implementação Desktop (Tabelas)

```css
/* Container de Nome/Título */
.text-container-desktop {
    display: flex;
    align-items: center;
    space-x: 0.75rem;
}

.icon-container {
    flex-shrink: 0;              /* Impede que o ícone encolha */
    width: 2rem;
    height: 2rem;
    background: bg-neutral-100 dark:bg-neutral-600;
    border-radius: rounded-lg;
    display: flex;
    align-items: center;
    justify-content: center;
}

.text-content {
    min-width: 0;                /* Permite que o texto seja truncado */
    flex: 1;                     /* Ocupa espaço disponível */
}

.text-title {
    font-size: text-sm;
    font-weight: font-medium;
    color: text-neutral-900 dark:text-white;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;         /* Força uma linha */
}

/* Container de Descrição */
.description-container {
    max-width: max-w-xs;         /* Limita largura (20rem) */
}

.description-text {
    font-size: text-sm;
    color: text-neutral-600 dark:text-neutral-400;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

#### Exemplo HTML Desktop:
```html
<td class="px-4 py-3">
  <div class="flex items-center space-x-3">
    <div class="w-8 h-8 bg-neutral-100 dark:bg-neutral-600 rounded-lg flex items-center justify-center flex-shrink-0">
      <!-- Ícone aqui -->
    </div>
    <div class="min-w-0 flex-1">
      <p class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ item.name }}">{{ item.name }}</p>
    </div>
  </div>
</td>
<td class="px-4 py-3">
  <div class="max-w-xs">
    <p class="text-sm text-neutral-600 dark:text-neutral-400 truncate" title="{{ item.description }}">{{ item.description }}</p>
  </div>
</td>
```

### Implementação Mobile (Cards)

```css
/* Container Principal do Card */
.mobile-card-header {
    display: flex;
    align-items: center;
    space-x: 0.5rem;
    min-width: 0;                /* Permite truncamento */
    flex: 1;
}

.mobile-icon {
    flex-shrink: 0;              /* Ícone não encolhe */
    width: 1.5rem;
    height: 1.5rem;
}

.mobile-content {
    min-width: 0;                /* Permite que o conteúdo seja truncado */
    flex: 1;
}

.mobile-title {
    font-size: text-sm;
    font-weight: font-medium;
    color: text-neutral-900 dark:text-white;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Descrição com múltiplas linhas */
.mobile-description {
    font-size: text-xs;
    color: text-neutral-600 dark:text-neutral-400;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;       /* Máximo 2 linhas */
    overflow: hidden;
    text-overflow: ellipsis;
}
```

#### Exemplo HTML Mobile:
```html
<div class="flex items-center space-x-2 min-w-0 flex-1">
  <div class="w-6 h-6 bg-white dark:bg-neutral-600 rounded flex items-center justify-center flex-shrink-0">
    <!-- Ícone aqui -->
  </div>
  <div class="min-w-0 flex-1">
    <h4 class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ item.name }}">{{ item.name }}</h4>
  </div>
</div>

<!-- Descrição com line-clamp -->
<p class="text-xs text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2" title="{{ item.description }}">{{ item.description }}</p>
```

### Classes CSS Customizadas Obrigatórias

```css
/* Classes para line-clamp (suporte a múltiplas linhas) */
.line-clamp-1 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 1;
    overflow: hidden;
    text-overflow: ellipsis;
}

.line-clamp-2 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    text-overflow: ellipsis;
}

.line-clamp-3 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Classes utilitárias para containers flexíveis */
.text-container {
    min-width: 0;
    flex: 1;
}

.icon-fixed {
    flex-shrink: 0;
}

/* Larguras máximas padrão para descrições */
.max-w-description-sm { max-width: 12rem; }  /* 192px */
.max-w-description-md { max-width: 16rem; }  /* 256px */
.max-w-description-lg { max-width: 20rem; }  /* 320px */
```

### Diretrizes de Implementação

#### 1. **Elementos Obrigatórios para Ellipsis:**
- Nomes de produtos/categorias/usuários
- Descrições de qualquer tamanho
- Endereços e textos longos
- Comentários e observações
- Qualquer campo de texto livre

#### 2. **Elementos que NÃO precisam de ellipsis:**
- Números (preços, quantidades, IDs)
- Datas e horários
- Status e badges
- Botões e links de ação
- Textos fixos do sistema

#### 3. **Estrutura Padrão para Tabelas:**
```html
<td class="px-4 py-3">
  <div class="flex items-center space-x-3">
    <div class="w-8 h-8 bg-neutral-100 dark:bg-neutral-600 rounded-lg flex items-center justify-center flex-shrink-0">
      <!-- Ícone/Avatar -->
    </div>
    <div class="min-w-0 flex-1">
      <p class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ full_text }}">{{ display_text }}</p>
    </div>
  </div>
</td>
```

#### 4. **Estrutura Padrão para Cards Mobile:**
```html
<div class="flex items-center space-x-2 min-w-0 flex-1">
  <div class="w-6 h-6 bg-white dark:bg-neutral-600 rounded flex items-center justify-center flex-shrink-0">
    <!-- Ícone -->
  </div>
  <div class="min-w-0 flex-1">
    <h4 class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ full_title }}">{{ title }}</h4>
  </div>
</div>

<!-- Para descrições com múltiplas linhas -->
<p class="text-xs text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2" title="{{ full_description }}">{{ description }}</p>
```

### Regras de Aplicação

#### ✅ **SEMPRE FAZER:**
1. Adicionar `title="{{ campo_completo }}"` em elementos com ellipsis
2. Usar `flex-shrink-0` em ícones e elementos que não devem encolher
3. Aplicar `min-w-0 flex-1` em containers de texto
4. Definir larguras máximas para descrições (`max-w-xs`, `max-w-sm`, etc.)
5. Testar com textos muito longos (>100 caracteres)

#### ❌ **NUNCA FAZER:**
1. Deixar textos longos sem controle de overflow
2. Esquecer do `title` attribute
3. Permitir que ícones sejam comprimidos
4. Usar larguras fixas que quebram em diferentes resoluções
5. Implementar ellipsis sem testar responsividade

### Exemplo Completo de Template

```html
<!-- categories.html - Exemplo de implementação correta -->

<!-- Versão Desktop - Tabela -->
<tr class="category-row hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-150">
  <!-- Coluna Nome -->
  <td class="px-4 py-3">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 bg-neutral-100 dark:bg-neutral-600 rounded-lg flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-neutral-600 dark:text-neutral-400">...</svg>
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ category.name }}">{{ category.name }}</p>
      </div>
    </div>
  </td>
  
  <!-- Coluna Descrição -->
  <td class="px-4 py-3">
    <div class="max-w-xs">
      {% if category.description %}
        <p class="text-sm text-neutral-600 dark:text-neutral-400 truncate" title="{{ category.description }}">{{ category.description }}</p>
      {% else %}
        <span class="text-neutral-400 dark:text-neutral-500 italic">Sem descrição</span>
      {% endif %}
    </div>
  </td>
</tr>

<!-- Versão Mobile - Card -->
<div class="category-card bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3 border border-neutral-200 dark:border-neutral-600">
  <!-- Header do Card -->
  <div class="flex items-start justify-between mb-2">
    <div class="flex items-center space-x-2 min-w-0 flex-1">
      <div class="w-6 h-6 bg-white dark:bg-neutral-600 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-3 h-3 text-neutral-600 dark:text-neutral-400">...</svg>
      </div>
      <div class="min-w-0 flex-1">
        <h4 class="text-sm font-medium text-neutral-900 dark:text-white truncate" title="{{ category.name }}">{{ category.name }}</h4>
      </div>
    </div>
  </div>
  
  <!-- Descrição -->
  {% if category.description %}
  <p class="text-xs text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2" title="{{ category.description }}">{{ category.description }}</p>
  {% endif %}
</div>
```

### Checklist de Validação

Antes de considerar uma tela concluída, verificar:

- [ ] **Nomes longos** (>50 caracteres) são truncados com ellipsis
- [ ] **Descrições longas** (>100 caracteres) são truncadas apropriadamente
- [ ] **Title attributes** estão presentes em todos os elementos truncados
- [ ] **Ícones não encolhem** em telas pequenas
- [ ] **Layout não quebra** com textos de 200+ caracteres
- [ ] **Mobile e desktop** funcionam corretamente
- [ ] **Dark mode** mantém a funcionalidade
- [ ] **Hover nos tooltips** mostra texto completo

---

## 🎭 Estados e Interações Avançadas

### Sistema de Hover States
```css
/* Navegação */
.nav-item-hover {
    transform: translateX(4px);
    transition: all 0.2s ease-in-out;
    background: hover:bg-neutral-100 dark:hover:bg-neutral-700;
}

/* Botões */
.button-hover {
    background: hover:bg-neutral-200 dark:hover:bg-neutral-600;
    box-shadow: hover:shadow-md;
    transform: hover:translateY(-1px);
    transition: all 0.2s ease-in-out;
}

/* Cards */
.card-hover {
    box-shadow: hover:shadow-md;
    transform: hover:scale(1.01);
    transition: all 0.2s ease-in-out;
}

/* Linhas de Tabela */
.table-row-hover {
    background: hover:bg-neutral-50 dark:hover:bg-neutral-700;
    transition: background-color 0.15s ease-in-out;
}
```

### Focus States para Acessibilidade
```css
/* Inputs */
.input-focus {
    outline: none;
    ring: ring-2 ring-neutral-500 dark:ring-neutral-400;
    border: border-transparent;
    transition: all 0.2s ease-in-out;
}

/* Botões */
.button-focus {
    outline: none;
    ring: ring-2 ring-neutral-500 dark:ring-neutral-400;
    ring-offset: ring-offset-2;
}

/* Links */
.link-focus {
    outline: none;
    ring: ring-2 ring-neutral-500 dark:ring-neutral-400;
    ring-offset: ring-offset-1;
    border-radius: rounded;
}
```

### Transições e Animações
```css
/* Durações Padrão */
.transition-fast { transition: all 0.2s ease-in-out; }          /* Hovers rápidos */
.transition-medium { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }  /* Mudanças de tema */
.transition-slow { transition: all 0.5s ease-in-out; }          /* Animações complexas */

/* Propriedades Específicas */
.transition-colors { transition: color, background-color, border-color 0.2s ease-in-out; }
.transition-transform { transition: transform 0.2s ease-in-out; }
.transition-shadow { transition: box-shadow 0.2s ease-in-out; }

/* Easing Functions */
.ease-out-cubic { transition-timing-function: cubic-bezier(0.33, 1, 0.68, 1); }
.ease-in-out-cubic { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }
```

---

## 🎨 Sistema de Sombras e Elevação

### Hierarquia de Elevação
```css
/* Sombras Base */
shadow-xs: 0 1px 1px 0 rgb(0 0 0 / 0.03)      /* Micro elevação */
shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)      /* Bordas sutis */
shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)    /* Elevação média */
shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1)  /* Elevação alta */
shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1)  /* Elevação máxima */

/* Sombras Internas */
shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.06)

/* Sombras Coloridas */
shadow-neutral: 0 4px 6px -1px rgb(115 115 115 / 0.1)
shadow-red: 0 4px 6px -1px rgb(239 68 68 / 0.1)
shadow-green: 0 4px 6px -1px rgb(34 197 94 / 0.1)
```

### Aplicação por Componente
```css
/* Cards */
.card-base { box-shadow: shadow-sm; }
.card-elevated { box-shadow: shadow-md; }
.card-floating { box-shadow: shadow-lg; }

/* Botões */
.button-base { box-shadow: shadow-sm; }
.button-hover { box-shadow: shadow-md; }
.button-active { box-shadow: shadow-inner; }

/* Sidebar */
.sidebar-desktop { box-shadow: shadow-sm; }
.sidebar-mobile { box-shadow: shadow-xl; }

/* Modais */
.modal-overlay { box-shadow: shadow-xl; }
```

---

## 🔧 Implementação Técnica Detalhada

### Configuração Tailwind CSS
```javascript
// tailwind.config.js
module.exports = {
    darkMode: 'class',
    content: [
        './templates/**/*.html',
        './static/**/*.js'
    ],
    theme: {
        extend: {
            colors: {
                neutral: {
                    50: '#fafafa',
                    100: '#f5f5f5',
                    200: '#e5e5e5',
                    300: '#d4d4d4',
                    400: '#a3a3a3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717',
                    950: '#0a0a0a'
                }
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem'
            },
            height: {
                'screen-safe': '100vh',
                'screen-mobile': 'calc(100vh - 1rem)'
            }
        }
    },
    plugins: []
}
```

### CSS Customizado Essencial
```css
/* Variáveis CSS para Consistência */
:root {
    --header-height: 4rem;
    --sidebar-width: 16rem;
    --stats-height: auto;
    --pagination-height: 3.5rem;
    --mobile-padding: 0.75rem;
    --desktop-padding: 1.5rem;
}

/* Classes Utilitárias Customizadas */
.mobile-content-padding {
    padding: var(--mobile-padding);
}

@media (min-width: 768px) {
    .mobile-content-padding {
        padding: var(--desktop-padding);
    }
}

/* Layout Zero Scroll */
.zero-scroll-layout {
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.content-area {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.scrollable-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
}

/* Transições Personalizadas */
.sidebar-transition {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-transition {
    transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item {
    transition: all 0.2s ease-in-out;
}

.nav-item:hover {
    transform: translateX(4px);
}

/* Scrollbar Personalizada */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: theme('colors.neutral.100');
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: theme('colors.neutral.300');
    border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: theme('colors.neutral.400');
}

/* Dark Mode Scrollbar */
.dark .custom-scrollbar::-webkit-scrollbar-track {
    background: theme('colors.neutral.800');
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
    background: theme('colors.neutral.600');
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: theme('colors.neutral.500');
}
```

### JavaScript para Funcionalidades
```javascript
// Configuração Global
const AutoSellConfig = {
    animations: {
        fast: 200,
        medium: 300,
        slow: 500
    },
    breakpoints: {
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280
    },
    pagination: {
        defaultItems: 5,
        options: [5, 10, 25]
    }
};

// Dark Mode Toggle
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    // Verificar preferência salva
    const isDark = localStorage.getItem('darkMode') === 'true' || 
                   (!localStorage.getItem('darkMode') && 
                    window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    if (isDark) {
        html.classList.add('dark');
    }
    
    // Toggle functionality
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            html.classList.toggle('dark');
            localStorage.setItem('darkMode', html.classList.contains('dark'));
        });
    }
}

// Mobile Menu
function initMobileMenu() {
    const menuButton = document.getElementById('mobileMenuButton');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');
    
    function toggleMenu() {
        sidebar.classList.toggle('mobile-sidebar-open');
        overlay.classList.toggle('mobile-overlay-visible');
        document.body.classList.toggle('overflow-hidden');
    }
    
    if (menuButton) {
        menuButton.addEventListener('click', toggleMenu);
    }
    
    if (overlay) {
        overlay.addEventListener('click', toggleMenu);
    }
}

// Pagination System
class PaginationManager {
    constructor(options = {}) {
        this.currentPage = 1;
        this.itemsPerPage = options.itemsPerPage || AutoSellConfig.pagination.defaultItems;
        this.filteredItems = [];
        this.allItems = [];
        
        this.initElements();
        this.initEventListeners();
        this.initialize();
    }
    
    initElements() {
        this.productRows = document.querySelectorAll('.product-row');
        this.productCards = document.querySelectorAll('.product-card');
        this.searchInput = document.getElementById('searchInput');
        this.resultsInfo = document.getElementById('resultsInfo');
        this.itemsPerPageSelect = document.getElementById('itemsPerPage');
        this.prevButton = document.getElementById('prevPage');
        this.nextButton = document.getElementById('nextPage');
        this.pageNumbers = document.getElementById('pageNumbers');
    }
    
    initEventListeners() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.filterProducts(e.target.value.toLowerCase());
                this.currentPage = 1;
                this.render();
            });
        }
        
        if (this.itemsPerPageSelect) {
            this.itemsPerPageSelect.addEventListener('change', (e) => {
                this.itemsPerPage = parseInt(e.target.value);
                this.currentPage = 1;
                this.render();
            });
        }
        
        if (this.prevButton) {
            this.prevButton.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.render();
                }
            });
        }
        
        if (this.nextButton) {
            this.nextButton.addEventListener('click', () => {
                const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.render();
                }
            });
        }
    }
    
    initialize() {
        this.allItems = Array.from(this.productRows.length > 0 ? this.productRows : this.productCards);
        this.filteredItems = [...this.allItems];
        this.render();
    }
    
    filterProducts(searchTerm) {
        if (searchTerm === '') {
            this.filteredItems = [...this.allItems];
        } else {
            this.filteredItems = this.allItems.filter(item => {
                const name = item.dataset.name || '';
                const price = item.dataset.price || '';
                const id = item.dataset.id || '';
                
                return name.includes(searchTerm) || 
                       price.includes(searchTerm) || 
                       id.includes(searchTerm);
            });
        }
    }
    
    render() {
        this.renderItems();
        this.renderPagination();
        this.updateResultsInfo();
    }
    
    renderItems() {
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        
        // Ocultar todos os itens
        this.allItems.forEach(item => item.style.display = 'none');
        
        // Mostrar apenas itens filtrados e paginados
        this.filteredItems.slice(startIndex, endIndex).forEach(item => {
            item.style.display = '';
        });
        
        // Atualizar controles de navegação
        if (this.prevButton) {
            this.prevButton.disabled = this.currentPage === 1;
        }
        
        if (this.nextButton) {
            this.nextButton.disabled = this.currentPage === totalPages || totalPages === 0;
        }
    }
    
    renderPagination() {
        if (!this.pageNumbers) return;
        
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        this.pageNumbers.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        // Mostrar máximo 5 números de página
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.className = `px-3 py-1.5 text-sm font-medium rounded transition-colors duration-200 ${
                i === this.currentPage 
                    ? 'bg-neutral-900 dark:bg-white text-white dark:text-neutral-900' 
                    : 'border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700'
            }`;
            
            pageButton.addEventListener('click', () => {
                this.currentPage = i;
                this.render();
            });
            
            this.pageNumbers.appendChild(pageButton);
        }
    }
    
    updateResultsInfo() {
        if (!this.resultsInfo) return;
        
        const totalItems = this.filteredItems.length;
        const startIndex = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endIndex = Math.min(this.currentPage * this.itemsPerPage, totalItems);
        
        if (totalItems === 0) {
            this.resultsInfo.textContent = 'Nenhum produto encontrado';
        } else {
            this.resultsInfo.textContent = `Mostrando ${startIndex}-${endIndex} de ${totalItems} produtos`;
        }
    }
}

// Inicialização Global
document.addEventListener('DOMContentLoaded', function() {
    initDarkMode();
    initMobileMenu();
    
    // Inicializar paginação se existirem produtos
    const hasProducts = document.querySelectorAll('.product-row, .product-card').length > 0;
    if (hasProducts) {
        new PaginationManager();
    }
});
```

---

## 📋 Padrões de Implementação

### Estrutura de Arquivos Recomendada
```
autosell/
├── templates/
│   ├── base.html                 # Layout base
│   ├── dashboard.html            # Layout principal com sidebar
│   ├── products/
│   │   ├── products.html         # Lista com paginação
│   │   ├── product.html          # Detalhes do produto
│   │   ├── create_product.html   # Formulário de criação
│   │   ├── edit_product.html     # Formulário de edição
│   │   └── confirm_delete.html   # Confirmação de exclusão
│   └── categories/
│       └── categories.html       # Lista de categorias
├── static/
│   ├── css/
│   │   ├── tailwind.css          # Tailwind compilado
│   │   └── custom.css            # Estilos customizados
│   └── js/
│       ├── main.js               # JavaScript principal
│       ├── pagination.js         # Sistema de paginação
│       └── mobile.js             # Funcionalidades mobile
└── docs/
    └── autosell-complete-style-guide.md
```

### Nomenclatura de Classes
```css
/* Convenções de Nomenclatura */
.component-name { }               /* Componente principal */
.component-name__element { }      /* Elemento do componente */
.component-name--modifier { }     /* Modificador do componente */

/* Exemplos Práticos */
.stats-card { }                   /* Card de estatísticas */
.stats-card__number { }           /* Número dentro do card */
.stats-card--compact { }          /* Versão compacta do card */

.pagination { }                   /* Container de paginação */
.pagination__button { }           /* Botão de paginação */
.pagination__button--active { }   /* Botão ativo */
```

### Organização do Código HTML
```html
<!-- Estrutura Recomendada -->
<!DOCTYPE html>
<html lang="pt-BR" class="h-full">
<head>
    <!-- Meta tags essenciais -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoSell - {{ page_title }}</title>
    
    <!-- CSS -->
    <link href="{% static 'css/tailwind.css' %}" rel="stylesheet">
    
    <!-- Configuração inicial -->
    <script>
        // Verificar dark mode antes do carregamento
        if (localStorage.getItem('darkMode') === 'true') {
            document.documentElement.classList.add('dark');
        }
    </script>
</head>
<body class="h-full bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-white">
    <!-- Layout principal -->
    <div class="h-full flex">
        <!-- Sidebar -->
        <aside class="sidebar">...</aside>
        
        <!-- Conteúdo principal -->
        <main class="flex-1 flex flex-col overflow-hidden">
            <!-- Header -->
            <header class="header-compact">...</header>
            
            <!-- Stats -->
            <section class="stats-compact">...</section>
            
            <!-- Conteúdo -->
            <section class="content-main">...</section>
            
            <!-- Paginação -->
            <footer class="pagination-footer">...</footer>
        </main>
    </div>
    
    <!-- JavaScript -->
    <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

---

## 🎯 Checklist de Implementação Completo

### ✅ Layout e Estrutura
- [ ] Layout flexbox com altura 100vh
- [ ] Header compacto com título e ações
- [ ] Cards de estatísticas com padding reduzido
- [ ] Área de conteúdo com flex-1 e overflow hidden
- [ ] Paginação fixa no rodapé

### ✅ Responsividade Mobile
- [ ] Breakpoints mobile-first implementados
- [ ] Menu mobile com sidebar deslizante
- [ ] Botões e inputs adaptados para touch
- [ ] Cards em grid 2x2 no mobile
- [ ] Paginação responsiva
- [ ] **Text overflow ellipsis implementado**
- [ ] **Title attributes em elementos truncados**
- [ ] **Flexbox responsivo (min-w-0, flex-1, flex-shrink-0)**
- [ ] **Classes line-clamp para descrições mobile**
- [ ] **Larguras máximas definidas para containers de texto**

### ✅ Sistema de Cores
- [ ] Paleta neutral 50-900 aplicada
- [ ] Dark mode funcionando
- [ ] Estados hover e focus
- [ ] Cores de feedback (verde, vermelho, azul)

### ✅ Tipografia
- [ ] Hierarquia de textos definida
- [ ] Tamanhos responsivos (text-sm, text-xs)
- [ ] Pesos de fonte consistentes
- [ ] Legibilidade em ambos os modos

### ✅ Componentes
- [ ] Botões com estados visuais
- [ ] Formulários com validação
- [ ] Tabelas responsivas
- [ ] Cards com elevação
- [ ] Badges de status

### ✅ Funcionalidades JavaScript
- [ ] Paginação com números de página
- [ ] Busca em tempo real
- [ ] Controle de itens por página
- [ ] Contador de resultados
- [ ] Navegação por teclado

### ✅ Performance
- [ ] Transições GPU-accelerated
- [ ] CSS otimizado
- [ ] JavaScript eficiente
- [ ] Imagens otimizadas

### ✅ Acessibilidade
- [ ] Contraste adequado
- [ ] Estados de foco visíveis
- [ ] Navegação por teclado
- [ ] Labels associados
- [ ] Textos alternativos

---

## 🔄 Manutenção e Evolução

### Atualizações de Design
1. **Manter Consistência**: Sempre usar a paleta neutral e espaçamentos definidos
2. **Testar Responsividade**: Verificar em diferentes dispositivos
3. **Validar Dark Mode**: Garantir que novos componentes funcionem nos dois modos
4. **Preservar Zero Scroll**: Manter layouts com altura fixa

### Adição de Novas Páginas
1. **Seguir Template**: Usar a estrutura de `products.html` como base
2. **Implementar Paginação**: Para listas com mais de 5 itens
3. **Adaptar Mobile**: Criar versões específicas para mobile
4. **Aplicar Ellipsis**: Implementar text overflow em todos os campos de texto
5. **Adicionar Tooltips**: Incluir title attributes em elementos truncados
6. **Documentar Mudanças**: Atualizar este guia quando necessário

### Novos Componentes
1. **Seguir Padrões**: Usar classes Tailwind existentes
2. **Implementar Estados**: Hover, focus, active, disabled
3. **Testar Acessibilidade**: Verificar contraste e navegação
4. **Otimizar Performance**: Usar transições eficientes

---

## 📊 Métricas de Qualidade

### Performance Targets
- **First Paint**: < 1s
- **Time to Interactive**: < 2s
- **Layout Shift**: < 0.1
- **Bundle Size**: < 100KB

### Acessibilidade Targets
- **Contraste**: WCAG AA (4.5:1)
- **Navegação por Teclado**: 100%
- **Screen Reader**: Compatível
- **Touch Targets**: >= 44px

### Responsividade Targets
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+
- **Layout Quebras**: 0

---

## 🏆 Conclusão

Este guia completo define todos os aspectos do design system do AutoSell, garantindo consistência, performance e usabilidade em todas as interfaces. Seguindo estas diretrizes, qualquer desenvolvedor pode criar interfaces que se integram perfeitamente ao sistema existente.

**Princípios-chave para lembrar:**
1. **Zero Scroll**: Layouts devem ocupar 100% da viewport
2. **Mobile-First**: Sempre pensar primeiro no mobile
3. **Neutral Palette**: Usar apenas a escala neutral
4. **5-Item Pagination**: Paginação padrão com 5 itens
5. **Consistent Spacing**: Múltiplos de 4px sempre
6. **Text Overflow Ellipsis**: Controlar overflow de texto com tooltips obrigatórios

---

**Versão**: 2.0  
**Data**: Janeiro 2025  
**Equipe**: Design & Development AutoSell  
**Status**: Implementado e Validado ✅
