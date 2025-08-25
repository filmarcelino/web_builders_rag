
# React Básico

React é uma biblioteca JavaScript para construir interfaces de usuário.

## Componentes

```jsx
// Componente funcional
function MeuComponente(props) {
    return (
        <div>
            <h1>Olá, {props.nome}!</h1>
        </div>
    );
}

// Componente com hooks
import React, { useState } from 'react';

function Contador() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Você clicou {count} vezes</p>
            <button onClick={() => setCount(count + 1)}>
                Clique aqui
            </button>
        </div>
    );
}
```

## Props e State

- **Props**: Dados passados de componente pai para filho
- **State**: Dados internos do componente que podem mudar
