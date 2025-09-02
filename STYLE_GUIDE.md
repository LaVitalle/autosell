# 🎨 Dashboard Style Guide - AutoSell

## 📋 Visão Geral
Este documento descreve detalhadamente o sistema de design, paleta de cores, tipografia e componentes utilizados no dashboard do AutoSell, seguindo princípios de design minimalista com foco em usabilidade e acessibilidade.

## 🎯 Princípios de Design

### Minimalismo
- **Simplicidade**: Interface limpa sem elementos desnecessários
- **Hierarquia visual**: Organização clara de informações
- **Espaçamento**: Uso generoso de whitespace para respiração visual
- **Foco**: Cada elemento tem um propósito claro

### Usabilidade
- **Intuitividade**: Navegação clara e previsível
- **Consistência**: Padrões uniformes em todo o sistema
- **Feedback visual**: Estados hover e transições suaves
- **Responsividade**: Adaptação para diferentes tamanhos de tela

## 🎨 Sistema de Cores

### Paleta Neutra (Neutral Color Palette)
```css
/* Cores Base */
neutral-50:  #fafafa    /* Fundo principal - modo claro */
neutral-100: #f5f5f5   /* Fundos secundários */
neutral-200: #e5e5e5   /* Bordas e divisores */
neutral-300: #d4d4d4   /* Bordas sutis */
neutral-400: #a3a3a3   /* Textos secundários */
neutral-500: #737373    /* Textos médios */
neutral-600: #525252    /* Textos importantes */
neutral-700: #404040    /* Fundos escuros */
neutral-800: #262626    /* Sidebar escura */
neutral-900: #171717    /* Fundo principal - modo escuro */
neutral-950: #0a0a0a    /* Fundos muito escuros */
```

### Modo Claro vs Modo Escuro
- **Modo Claro**: Fundo `neutral-50`, textos `neutral-900`
- **Modo Escuro**: Fundo `neutral-900`, textos `neutral-50`
- **Transições**: Duração de 300ms com easing `cubic-bezier(0.4, 0, 0.2, 1)`

## 🔤 Tipografia

### Hierarquia de Textos
```css
/* Títulos */
h1: text-xl font-semibold          /* Logo da sidebar */
h2: text-3xl font-bold            /* Título principal do dashboard */

/* Navegação */
nav-text: text-sm font-medium     /* Itens de menu */
nav-text-hover: font-medium       /* Estado hover */

/* Conteúdo */
body-text: text-sm                /* Texto padrão */
caption: text-xs                  /* Textos pequenos (email do usuário) */
stats: text-2xl font-bold         /* Números das estatísticas */
```

### Fontes
- **Sistema**: Fontes do sistema operacional para melhor performance
- **Peso**: Combinação de `font-medium` e `font-bold` para hierarquia
- **Tamanhos**: Escala consistente baseada em múltiplos de 4px

## 🧩 Componentes

### Sidebar
```css
/* Container */
width: 16rem (w-64)
background: white/dark:neutral-800
border-right: 1px solid neutral-200/dark:neutral-700
shadow: shadow-sm
padding: 1.5rem (p-6)

/* Logo */
logo-container: w-8 h-8 rounded-lg
logo-text: text-lg font-bold

/* Navegação */
nav-item: p-3 rounded-lg
nav-item-hover: hover:bg-neutral-100/dark:neutral-700
nav-item-text: text-neutral-700/dark:neutral-300
nav-item-hover-text: hover:text-neutral-900/dark:text-white

/* Usuário */
user-section: border-t border-neutral-200/dark:neutral-700
user-avatar: w-8 h-8 rounded-full
```

### Cards de Estatísticas
```css
/* Container */
background: white/dark:neutral-800
border: 1px solid neutral-200/dark:neutral-700
border-radius: 0.75rem (rounded-xl)
padding: 1.5rem (p-6)
shadow: shadow-sm

/* Layout */
grid: grid-cols-1 md:grid-cols-3
gap: 1.5rem (gap-6)

/* Ícones */
icon-container: w-12 h-12 rounded-lg
icon-background: bg-neutral-100/dark:neutral-700
icon-size: w-6 h-6
icon-color: text-neutral-600/dark:text-neutral-400
```

### Toggle de Dark Mode
```css
/* Container */
background: neutral-100/dark:neutral-700
border-radius: 0.5rem (rounded-lg)
padding: 0.75rem (p-3)

/* Switch */
switch-width: 2.5rem (w-10)
switch-height: 1.5rem (h-6)
switch-background: neutral-300/dark:neutral-600
switch-border-radius: rounded-full

/* Círculo */
circle-size: 1.25rem (w-5 h-5)
circle-background: white
circle-shadow: shadow-sm
circle-transition: translate-x-0.5 (light) / translate-x-4 (dark)
```

## 🎭 Estados e Interações

### Hover States
```css
/* Navegação */
transform: translateX(4px)        /* Movimento sutil para direita */
transition: all 0.2s ease-in-out

/* Botões */
background: neutral-200/dark:neutral-600
transition: all 0.2s ease-in-out

/* Cards */
shadow: shadow-md (elevação sutil)
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

## 📱 Responsividade

### Breakpoints
```css
/* Mobile First */
default: < 768px
md: >= 768px

/* Sidebar Mobile */
mobile-sidebar: -translate-x-full (oculta)
mobile-menu-button: fixed top-4 left-4 z-50
```

### Grid System
```css
/* Cards de Estatísticas */
mobile: grid-cols-1
desktop: md:grid-cols-3

/* Layout Principal */
sidebar: w-64 (fixo)
content: flex-1 (flexível)
```

## 🎨 Sombras e Elevação

### Sistema de Sombras
```css
shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)    /* Bordas sutis */
shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)  /* Elevação média */
shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1) /* Elevação alta */
```

### Uso por Componente
- **Sidebar**: `shadow-sm` para separação sutil
- **Cards**: `shadow-sm` para elevação básica
- **Botões mobile**: `shadow-lg` para destaque

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

### JavaScript
```javascript
// Dark Mode Toggle
- localStorage para persistência
- classList.toggle para alternância
- Transições CSS para suavidade

// Responsividade
- Detecção de viewport
- Criação dinâmica de botão mobile
- Toggle de sidebar em dispositivos móveis
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

## 📐 Espaçamento e Layout

### Sistema de Espaçamento
```css
/* Base: 4px (0.25rem) */
p-3: 0.75rem (12px)
p-6: 1.5rem (24px)
p-8: 2rem (32px)

/* Margens */
mb-2: 0.5rem (8px)
mb-6: 1.5rem (24px)
mb-8: 2rem (32px)

/* Gaps */
gap-6: 1.5rem (24px)
space-y-2: 0.5rem (8px)
space-y-4: 1rem (16px)
```

### Layout Grid
```css
/* Container Principal */
flex h-full                    /* Layout flexbox vertical */
flex min-h-screen             /* Altura mínima da tela */

/* Sidebar + Content */
flex                          /* Layout flexbox horizontal */
w-64 + flex-1                /* Sidebar fixa + Content flexível */
```

## 🎯 Acessibilidade

### Contraste
- **Modo Claro**: Texto `neutral-900` sobre fundo `neutral-50` (contraste alto)
- **Modo Escuro**: Texto `neutral-50` sobre fundo `neutral-900` (contraste alto)

### Foco e Navegação
- Estados hover visíveis
- Transições suaves para mudanças de estado
- Estrutura semântica com `<aside>`, `<main>`, `<nav>`

### Responsividade
- Sidebar colapsável em dispositivos móveis
- Botão de menu acessível
- Layout adaptativo para diferentes tamanhos de tela

## 🚀 Performance

### Otimizações
- **CSS**: Transições GPU-accelerated
- **JavaScript**: Event listeners eficientes
- **Imagens**: Ícones SVG inline para melhor performance
- **Fontes**: Sistema fonts para carregamento rápido

### Lazy Loading
- Componentes criados dinamicamente apenas quando necessário
- Sidebar mobile criada sob demanda

---

*Este guia de estilo garante consistência visual e de comportamento em todo o dashboard, proporcionando uma experiência de usuário coesa e profissional.*
