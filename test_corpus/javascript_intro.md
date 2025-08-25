
# Introdução ao JavaScript

JavaScript é uma linguagem de programação que permite criar páginas web interativas.

## Variáveis

```javascript
// Declaração de variáveis
let nome = "João";
const idade = 25;
var cidade = "São Paulo";
```

## Funções

```javascript
// Função tradicional
function saudacao(nome) {
    return "Olá, " + nome + "!";
}

// Arrow function
const saudacaoArrow = (nome) => {
    return `Olá, ${nome}!`;
};
```

## DOM Manipulation

```javascript
// Selecionar elementos
const elemento = document.getElementById("meuId");
const elementos = document.querySelectorAll(".minhaClasse");

// Modificar conteúdo
elemento.textContent = "Novo texto";
elemento.innerHTML = "<strong>Texto em negrito</strong>";
```
