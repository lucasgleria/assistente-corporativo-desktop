# Ícones do Botão Inicial

Esta pasta é destinada para armazenar imagens personalizadas do botão inicial (widget flutuante).

## Como Usar

1. **Adicione suas imagens nesta pasta:**
   - Exemplo: `chat.png`, `send.png`, etc.

2. **Configure no `app/config.py`:**
   ```python
   "button": {
       "image_collapsed": "data/icons/chat.png",
       "image_expanded": "data/icons/send.png",
       "image_size": (32, 32),  # Opcional: tamanho específico
   }
   ```

## Formatos Suportados

- PNG (recomendado - suporta transparência)
- JPG/JPEG
- SVG
- BMP
- ICO

## Recomendações

- **Tamanho ideal:** 64x64 pixels ou maior (será redimensionado automaticamente)
- **Fundo transparente:** Use PNG com canal alpha para melhor resultado
- **Qualidade:** Imagens vetoriais (SVG) escalam melhor em diferentes tamanhos
- **Contraste:** Certifique-se que a imagem seja visível sobre o fundo do botão

## Exemplo de Estrutura

```
data/icons/
  ├── chat.png          # Ícone quando colapsado
  ├── send.png          # Ícone quando expandido
  └── README.md         # Este arquivo
```

## Notas

- Se a imagem não for encontrada, o sistema usa o ícone/texto de fallback configurado
- Caminhos podem ser relativos ao projeto ou absolutos
- A imagem será redimensionada automaticamente para caber no botão

