# 🎨 AutoSell - Manual de Marca & Design System

## 📋 Visão Geral da Marca

**AutoSell** é uma plataforma de gestão de produtos com foco em design minimalista, usabilidade e experiência do usuário moderna. A marca se destaca pela simplicidade visual, paleta de cores neutras e funcionalidade intuitiva.

---

## 🎯 Princípios de Design

### Filosofia da Marca
- **Minimalismo**: Interface limpa sem elementos desnecessários
- **Usabilidade**: Foco na experiência do usuário e facilidade de uso
- **Consistência**: Padrões uniformes em todo o sistema
- **Profissionalismo**: Aparência moderna e confiável
- **Acessibilidade**: Design inclusivo e legível

### Valores Visuais
- **Simplicidade**: Cada elemento tem um propósito claro
- **Elegância**: Estética refinada e contemporânea
- **Clareza**: Comunicação visual direta e objetiva
- **Responsividade**: Adaptação perfeita a todos os dispositivos

---

## 🎨 Sistema de Cores

### Paleta Principal (Neutral)
```css
/* Cores Base */
neutral-50:  #fafafa    /* Fundo principal - modo claro */
neutral-100: #f5f5f5   /* Fundos secundários e hover states */
neutral-200: #e5e5e5   /* Bordas e divisores */
neutral-300: #d4d4d4   /* Bordas sutis e inputs */
neutral-400: #a3a3a3   /* Textos secundários */
neutral-500: #737373    /* Textos médios */
neutral-600: #525252    /* Textos importantes */
neutral-700: #404040    /* Fundos escuros */
neutral-800: #262626    /* Cards e sidebar */
neutral-900: #171717    /* Fundo principal - modo escuro */
neutral-950: #0a0a0a    /* Fundos muito escuros */
```

### Cores de Estado
```css
/* Sucesso/Positivo */
green-100: #dcfce7     /* Fundo de badge de status */
green-500: #22c55e     /* Texto de badge de status */
green-600: #16a34a     /* Hover de badge de status */
green-800: #166534      /* Texto de badge dark mode */
green-900: #14532d      /* Fundo de badge dark mode */

/* Aviso/Perigo */
red-100: #fee2e2       /* Fundo de mensagens de erro */
red-400: #f87171       /* Texto de mensagens de erro */
red-500: #ef4444       /* Botões de ação destrutiva */
red-600: #dc2626       /* Hover de botões destrutivos */
red-800: #991b1b       /* Bordas de mensagens dark mode */
red-900: #7f1d1d       /* Fundos de mensagens dark mode */

/* Informação */
blue-100: #dbeafe      /* Fundo de badges informativos */
blue-500: #3b82f6      /* Texto de badges informativos */
blue-800: #1e40af      /* Texto dark mode */
blue-900: #1e3a8a      /* Fundo dark mode */
```

### Modo Claro vs Modo Escuro
- **Modo Claro**: Fundo `neutral-50`, textos `neutral-900`
- **Modo Escuro**: Fundo `neutral-900`, textos `neutral-50`
- **Transições**: Duração de 200-300ms com easing `cubic-bezier(0.4, 0, 0.2, 1)`

---

## 🔤 Tipografia

### Hierarquia de Textos
```css
/* Títulos Principais */
h1: text-3xl font-bold          /* Títulos de página */
h2: text-3xl font-bold          /* Títulos de seção */
h3: text-lg font-semibold       /* Subtítulos de seção */

/* Navegação */
nav-text: text-sm font-medium   /* Itens de menu */
nav-text-hover: font-medium     /* Estado hover */

/* Conteúdo */
body-text: text-sm              /* Texto padrão */
caption: text-xs                /* Textos pequenos (metadados) */
stats: text-2xl font-bold       /* Números das estatísticas */
```

### Fontes
- **Sistema**: Fontes do sistema operacional para melhor performance
- **Peso**: Combinação de `font-medium` e `font-bold` para hierarquia
- **Tamanhos**: Escala consistente baseada em múltiplos de 4px
- **Altura de linha**: `leading-relaxed` para melhor legibilidade

---

## 🧩 Componentes do Sistema

### 1. Header Section
```css
/* Container */
max-width: max-w-4xl mx-auto
margin-bottom: mb-8

/* Título com Ícone */
flex items-center space-x-3 mb-2
icon-container: w-10 h-10 bg-neutral-100 dark:bg-neutral-700 rounded-lg
icon-size: w-6 h-6 text-neutral-600 dark:text-neutral-400
title: text-3xl font-bold text-neutral-900 dark:text-white
subtitle: text-neutral-600 dark:text-neutral-400
```

### 2. Cards
```css
/* Container Principal */
background: bg-white dark:bg-neutral-800
border-radius: rounded-xl
border: border border-neutral-200 dark:border-neutral-700
shadow: shadow-sm
overflow: hidden

/* Header do Card */
padding: px-6 py-4
border-bottom: border-b border-neutral-200 dark:border-neutral-700
title: text-lg font-semibold text-neutral-900 dark:text-white

/* Conteúdo do Card */
padding: p-6
spacing: space-y-6
```

### 3. Formulários
```css
/* Labels */
text-sm font-medium text-neutral-700 dark:text-neutral-300
margin-bottom: mb-2

/* Inputs */
w-full px-4 py-3 rounded-lg
border: border-neutral-300 dark:border-neutral-600
background: bg-white dark:bg-neutral-700
text: text-neutral-900 dark:text-white
placeholder: placeholder-neutral-500 dark:placeholder-neutral-400
focus: focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400
transition: transition-colors duration-200

/* Textarea */
rows: rows="4"
resize: resize-none

/* File Input */
file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
file:text-sm file:font-medium file:bg-neutral-100 dark:file:bg-neutral-600
file:text-neutral-700 dark:file:text-neutral-300
hover:file:bg-neutral-200 dark:hover:file:bg-neutral-500
```

### 4. Botões
```css
/* Botão Primário */
inline-flex items-center justify-center px-6 py-3
bg-neutral-900 dark:bg-white text-white dark:text-neutral-900
font-medium rounded-lg
hover:bg-neutral-800 dark:hover:bg-neutral-100
transition-all duration-200 shadow-sm hover:shadow-md

/* Botão Secundário */
inline-flex items-center justify-center px-6 py-3
border border-neutral-300 dark:border-neutral-600
text-neutral-700 dark:text-neutral-300 font-medium rounded-lg
hover:bg-neutral-50 dark:hover:bg-neutral-700
transition-all duration-200

/* Botão de Ação Destrutiva */
bg-red-600 dark:bg-red-500 text-white
hover:bg-red-700 dark:hover:bg-red-600
```

### 5. Tabelas
```css
/* Container */
overflow-x-auto

/* Header */
thead: bg-neutral-50 dark:bg-neutral-700
th: px-6 py-4 text-left text-sm font-medium text-neutral-700 dark:text-neutral-300 uppercase tracking-wider

/* Linhas */
tbody: divide-y divide-neutral-200 dark:divide-neutral-700
tr: hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-150
td: px-6 py-4

/* Células com Ícones */
flex items-center space-x-3
icon-container: w-10 h-10 bg-neutral-100 dark:bg-neutral-600 rounded-lg
icon-size: w-5 h-5 text-neutral-600 dark:text-neutral-400
```

### 6. Badges de Status
```css
/* Status Ativo */
inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200

/* Status Informativo */
bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200

/* Ícone do Badge */
w-2 h-2 mr-1.5 fill-currentColor
```

### 7. Mensagens de Erro
```css
/* Container */
text-red-600 dark:text-red-400 text-sm mt-2
flex items-center

/* Ícone */
w-4 h-4 mr-1 fill-none stroke-currentColor

/* Texto */
text-red-600 dark:text-red-400
```

---

## 📐 Sistema de Espaçamento

### Base de 4px (0.25rem)
```css
/* Padding */
p-3: 0.75rem (12px)
p-4: 1rem (16px)
p-6: 1.5rem (24px)
p-8: 2rem (32px)

/* Margens */
mb-2: 0.5rem (8px)
mb-4: 1rem (16px)
mb-6: 1.5rem (24px)
mb-8: 2rem (32px)

/* Gaps */
gap-3: 0.75rem (12px)
gap-6: 1.5rem (24px)

/* Espaçamentos Verticais */
space-y-3: 0.75rem (12px)
space-y-6: 1.5rem (24px)
```

---

## 🎭 Estados e Interações

### Hover States
```css
/* Navegação */
transform: translateX(4px)
transition: all 0.2s ease-in-out

/* Botões */
background: neutral-200/dark:neutral-600
transition: all 0.2s ease-in-out

/* Cards */
shadow: shadow-md (elevação sutil)
```

### Focus States
```css
/* Inputs */
outline: none
ring: ring-2 ring-neutral-500 dark:ring-neutral-400
border: border-transparent

/* Botões */
ring: ring-2 ring-neutral-500 dark:ring-neutral-400
```

### Transições
```css
/* Durações */
fast: 0.2s ease-in-out          /* Hover e interações rápidas */
medium: 0.3s cubic-bezier(0.4, 0, 0.2, 1)  /* Mudanças de tema */

/* Propriedades */
all: transition-all
colors: transition-colors
transform: transition-transform
```

---

## 📱 Responsividade

### Breakpoints
```css
/* Mobile First */
default: < 768px
sm: >= 640px
md: >= 768px
lg: >= 1024px

/* Grid System */
mobile: grid-cols-1
desktop: md:grid-cols-2, md:grid-cols-3, md:grid-cols-4
```

### Layout Adaptativo
```css
/* Containers */
max-w-2xl: Para telas de confirmação
max-w-4xl: Para formulários e listas
max-w-7xl: Para dashboards

/* Flexbox Responsivo */
flex-col sm:flex-row: Empilhamento em mobile, horizontal em desktop
```

---

## 🎨 Sombras e Elevação

### Sistema de Sombras
```css
shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)    /* Bordas sutis */
shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)  /* Elevação média */
shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1) /* Elevação alta */
```

### Uso por Componente
- **Cards**: `shadow-sm` para elevação básica
- **Botões**: `shadow-sm` com `hover:shadow-md`
- **Sidebar**: `shadow-sm` para separação sutil

---

## 🔧 Implementação Técnica

### Tailwind CSS
```javascript
// Configuração personalizada
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: { /* Paleta neutral customizada */ }
        }
    }
}
```

### CSS Customizado
```css
/* Transições personalizadas */
.sidebar-transition {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-transition {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item {
    transition: all 0.2s ease-in-out;
}

.nav-item:hover {
    transform: translateX(4px);
}
```

---

## 🚀 Padrões de Implementação

### Estrutura de Arquivos
```
templates/
├── dashboard.html          # Layout base com sidebar
├── products/
│   ├── products.html       # Lista de produtos
│   ├── product.html        # Detalhes do produto
│   ├── create_product.html # Formulário de criação
│   ├── edit_product.html   # Formulário de edição
│   └── confirm_delete.html # Confirmação de exclusão
```

### Padrões de Nomenclatura
- **Classes CSS**: Seguir convenções Tailwind
- **IDs**: Usar kebab-case (ex: `darkModeToggle`)
- **Variáveis**: Usar camelCase (ex: `toggleSwitch`)

### Organização do Código
1. **Meta tags** e configurações
2. **CSS personalizado** e configurações Tailwind
3. **Header** com título e descrição
4. **Conteúdo principal** em cards
5. **Formulários** com validação
6. **Ações** e botões
7. **JavaScript** para funcionalidades

---

## 🎯 Acessibilidade

### Contraste
- **Modo Claro**: Texto `neutral-900` sobre fundo `neutral-50` (contraste alto)
- **Modo Escuro**: Texto `neutral-50` sobre fundo `neutral-900` (contraste alto)

### Navegação
- Estados hover visíveis
- Transições suaves para mudanças de estado
- Estrutura semântica com `<aside>`, `<main>`, `<nav>`

### Formulários
- Labels associados corretamente
- Mensagens de erro claras
- Estados de foco visíveis

---

## 📋 Checklist de Implementação

### ✅ Elementos Obrigatórios
- [ ] Paleta de cores neutras aplicada
- [ ] Dark mode implementado
- [ ] Transições suaves (200-300ms)
- [ ] Espaçamentos consistentes (múltiplos de 4px)
- [ ] Responsividade mobile-first
- [ ] Ícones SVG inline
- [ ] Estados hover e focus
- [ ] Mensagens de erro com ícones

### ✅ Padrões de Design
- [ ] Header com ícone e descrição
- [ ] Cards com bordas arredondadas
- [ ] Botões com estados visuais
- [ ] Formulários com validação
- [ ] Tabelas responsivas
- [ ] Badges de status
- [ ] Mensagens de confirmação

---

## 🔄 Manutenção e Evolução

### Atualizações de Design
- Manter consistência com a paleta neutral
- Preservar transições e animações
- Documentar mudanças no sistema
- Testar em ambos os modos (claro/escuro)

### Novos Componentes
- Seguir padrões estabelecidos
- Usar classes Tailwind existentes
- Implementar dark mode
- Testar responsividade

---

*Este manual garante consistência visual e comportamental em todo o sistema AutoSell, proporcionando uma experiência de usuário coesa e profissional.*

**Versão**: 1.0  
**Data**: Janeiro 2025  
**Equipe**: Design & Development AutoSell
