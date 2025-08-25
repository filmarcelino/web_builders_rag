
# Acessibilidade Web

A acessibilidade web garante que sites sejam usáveis por pessoas com deficiências.

## Princípios WCAG

1. **Perceptível**: Informação deve ser apresentada de forma que usuários possam perceber
2. **Operável**: Interface deve ser operável por todos os usuários
3. **Compreensível**: Informação e operação da interface devem ser compreensíveis
4. **Robusto**: Conteúdo deve ser robusto o suficiente para ser interpretado por tecnologias assistivas

## Boas Práticas

```html
<!-- Use alt text em imagens -->
<img src="logo.png" alt="Logo da empresa">

<!-- Use labels em formulários -->
<label for="email">Email:</label>
<input type="email" id="email" name="email">

<!-- Use headings hierárquicos -->
<h1>Título Principal</h1>
<h2>Subtítulo</h2>
<h3>Sub-subtítulo</h3>
```

## ARIA

ARIA (Accessible Rich Internet Applications) fornece semântica adicional:

```html
<button aria-label="Fechar modal" onclick="closeModal()">
    ×
</button>

<div role="alert" aria-live="polite">
    Mensagem de sucesso
</div>
```
