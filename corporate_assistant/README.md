# Assistente Corporativo Desktop

Um assistente inteligente offline para Windows que responde perguntas corporativas usando busca semântica avançada.

## 🚀 Características

- **100% Offline**: Funciona sem conexão com internet após configuração inicial
- **Busca Semântica**: Usa sentence-transformers para encontrar respostas similares
- **Interface Moderna**: Widget flutuante + janela de chat com PyQt6
- **Banco Escalável**: SQLite com SQLAlchemy (fácil migração para PostgreSQL)
- **Performance**: Resposta < 1s em máquinas modestas
- **Sistema Tray**: Fica sempre disponível na bandeja do sistema
- **Sistema de Feedback**: Botões 👍👎 para treinar e melhorar respostas (modo desenvolvimento)

## 📋 Requisitos

- Windows 10/11
- Python 3.10 ou superior
- 2GB RAM mínimo
- 1GB espaço em disco (para modelo NLP)

## 🛠️ Instalação

### 1. Clone/Baixe o Projeto
```bash
# Se usando git
git clone <repositorio>
cd corporate_assistant

# Ou extraia o arquivo ZIP no diretório desejado
```

### 2. Instale as Dependências
```bash
# Instale as dependências Python
pip install -r requirements.txt
```

### 3. Baixe o Modelo NLP (Obrigatório)
```bash
# Execute o script de download do modelo
python download_model.py
```

Este passo é **obrigatório** para funcionamento offline. O script baixa o modelo `all-MiniLM-L6-v2` (~90MB) para o diretório `data/model/`.

### 4. Execute a Aplicação
```bash
python main.py
```

## 🎯 Como Usar

### Primeira Execução
1. Execute `python main.py`
2. Aparecerá um widget flutuante no canto da tela
3. Clique no widget ou ícone da bandeja para abrir o chat
4. Digite suas perguntas e receba respostas instantâneas

### Adicionando Conteúdo
Por padrão, o sistema vem com algumas perguntas de exemplo. Para adicionar seu próprio conteúdo:

1. **Descomente a função seed_database()** em `main.py` (linhas 67-99)
2. **Edite os dados de exemplo** com suas perguntas/respostas corporativas
3. **Execute novamente** para popular o banco

### Interface
- **Widget Flutuante**: Sempre visível, clique para abrir chat
- **Janela de Chat**: Interface principal de conversação
- **Bandeja do Sistema**: Controle da aplicação (menu com botão direito)
- **Sistema de Feedback**: Botões 👍👎 em cada resposta (modo desenvolvimento)

## 🏗️ Arquitetura

```
corporate_assistant/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── download_model.py       # Script para baixar modelo NLP
├── app/
│   ├── config.py          # Configurações centralizadas
│   ├── database/          # Camada de dados
│   │   ├── connection.py  # Gerenciamento de conexão (Singleton)
│   │   ├── models.py      # Modelos ORM (SQLAlchemy)
│   │   └── repository.py  # CRUD e busca por similaridade
│   ├── core/              # Lógica de negócio
│   │   └── nlp_engine.py  # Engine de busca semântica
│   └── ui/                # Interface gráfica
│       ├── tray.py        # Ícone na bandeja
│       ├── floating_widget.py  # Widget flutuante
│       └── chat_window.py # Janela de chat
└── data/                  # Dados da aplicação
    ├── corporate_assistant.db  # Banco SQLite
    ├── model/             # Modelo sentence-transformers
    └── app.log           # Logs da aplicação
```

## ⚙️ Configuração

### Banco de Dados
O sistema usa SQLite por padrão. Para migrar para PostgreSQL:

1. Edite `app/config.py`:
```python
ACTIVE_DB = "postgresql"  # Mude de "sqlite"
```

2. Configure a URL de conexão PostgreSQL no mesmo arquivo
3. Instale o driver: `pip install psycopg2-binary`

### Modelo NLP
- **Padrão**: `all-MiniLM-L6-v2` (384 dimensões, ~90MB)
- **Localização**: `data/model/all-MiniLM-L6-v2/`
- **Threshold**: 0.5 (confiança mínima para resposta)

Edite `app/config.py` para ajustar configurações do modelo.

### Interface

Personalize cores, tamanhos e comportamento editando `UI_CONFIG` em `app/config.py`.

#### Personalização do Botão Inicial (Widget Flutuante)

Você pode personalizar o botão inicial editando `UI_CONFIG["floating_widget"]` em `app/config.py`:

```python
"floating_widget": {
    # Personalização do botão
    "button": {
        # Opção 1: Usar imagens (prioridade se especificado)
        "image_collapsed": None,     # Caminho para imagem quando colapsado (ex: "data/icons/chat.png")
        "image_expanded": None,      # Caminho para imagem quando expandido (ex: "data/icons/send.png")
        "image_size": None,          # Tamanho da imagem em pixels (None = usa tamanho do botão)
        # Opção 2: Usar emoji/texto (fallback se imagem não especificada)
        "icon_collapsed": "💬",      # Ícone quando colapsado (emoji ou texto)
        "icon_expanded": "➤",        # Ícone quando expandido
        # Dimensões
        "size": (30, 30),            # Tamanho do botão (largura, altura)
        "circular_size": 60,         # Tamanho do círculo flutuante
        "expanded_width": 350,       # Largura quando expandido
        "expanded_height": 50,       # Altura quando expandido
        # Tooltips
        "tooltip_collapsed": "Clique para expandir o chat",
        "tooltip_expanded": "Digite sua pergunta e pressione Enter"
    },
    # Cores do widget
    "colors": {
        "background_normal": "#1E3A5F",   # Fundo normal (azul escuro)
        "background_hover": "#2C5F8D",    # Fundo no hover (azul médio)
        "border_color": "#1E3A5F",        # Cor da borda
        "icon_color": "#FFFFFF",          # Cor do ícone (branco)
        "background_expanded": "#FFFFFF", # Fundo quando expandido
        "border_expanded": "#DEE2E6"      # Borda quando expandido
    },
    # Posicionamento
    "position": {
        "corner": "bottom-right",  # Canto: "bottom-right", "bottom-left", "top-right", "top-left"
        "margin": 20               # Margem do canto em pixels
    }
}
```

**Exemplos de Personalização:**

1. **Usar imagem personalizada (RECOMENDADO):**
   ```python
   "button": {
       "image_collapsed": "data/icons/chat.png",    # Caminho relativo ao projeto
       "image_expanded": "data/icons/send.png",     # Ou caminho absoluto: "C:/caminho/imagem.png"
       "image_size": (32, 32),                      # Tamanho específico da imagem (opcional)
       # Se as imagens não existirem, usa icon_collapsed/icon_expanded como fallback
   }
   ```
   
   **Formatos suportados:** PNG, JPG, JPEG, SVG, BMP, ICO, etc.
   
   **Dicas:**
   - Coloque suas imagens na pasta `data/icons/`
   - Use imagens com fundo transparente (PNG) para melhor resultado
   - Recomendado: 64x64 pixels ou maior para qualidade em alta DPI

2. **Mudar o ícone para texto (se não usar imagem):**
   ```python
   "icon_collapsed": "Chat",
   "icon_expanded": "Enviar"
   ```

3. **Mudar as cores para tema verde:**
   ```python
   "background_normal": "#28A745",
   "background_hover": "#34CE57",
   "border_color": "#1E7E34"
   ```

4. **Mudar posição para canto superior esquerdo:**
   ```python
   "corner": "top-left",
   "margin": 30
   ```

5. **Aumentar o tamanho do círculo:**
   ```python
   "circular_size": 80,
   "size": (40, 40)
   ```

## 🔧 Desenvolvimento

### Estrutura Modular
- **Database**: Padrão Repository com SQLAlchemy ORM
- **NLP**: Engine isolado com cache de embeddings
- **UI**: Componentes PyQt6 com sinais/slots
- **Config**: Configurações centralizadas
- **Feedback**: Sistema de treinamento com análise de qualidade

### Sistema de Feedback e Aprendizado (Desenvolvimento)
O sistema inclui funcionalidades para coletar feedback e **aprender em tempo real**:

```bash
# Visualizar estatísticas de feedback
python view_feedback_stats.py

# Testar aprendizado em tempo real
python test_singleton_learning.py

# Testar persistência do aprendizado
python test_learning_persistence.py

# Limpar aprendizado (resetar)
python clear_learning.py

# Preparar para produção (remove feedback)
python disable_feedback.py
```

**Funcionalidades do Feedback:**
- Botões 👍👎 em cada resposta do assistente
- **Aprendizado instantâneo**: Thumbs down penaliza a resposta imediatamente
- **Singleton Engine**: Garante que o aprendizado persiste durante toda a sessão
- **Persistência entre sessões**: Botões para salvar/carregar aprendizado
- **Carregamento automático**: Restaura aprendizado salvo ao iniciar
- **Penalidades inteligentes**: Aplica-se a perguntas similares (85%+ similaridade)
- **Controles na interface**: Salvar, Carregar, Limpar e Info do aprendizado
- Coleta automática de embeddings das perguntas
- Análise de FAQs problemáticas
- Exportação de dados para treinamento
- Estatísticas de satisfação do usuário

### Adicionando Funcionalidades
1. **Novos tipos de pergunta**: Edite `models.py` e `repository.py`
2. **Melhor NLP**: Troque o modelo em `config.py`
3. **Nova UI**: Adicione componentes em `app/ui/`
4. **Análise de feedback**: Use `view_feedback_stats.py`

### Testes
```bash
# Teste completo do sistema
python test_system.py

# Teste conexão com banco
python -c "from app.database.connection import DatabaseManager; print('OK' if DatabaseManager().test_connection() else 'ERRO')"

# Teste modelo NLP
python -c "from app.core.nlp_engine import SearchEngine; print('OK' if SearchEngine().is_available() else 'ERRO')"

# Análise de feedback (desenvolvimento)
python view_feedback_stats.py
```

## 🐛 Solução de Problemas

### Modelo não encontrado
```
⚠ Modelo não encontrado em: data/model/all-MiniLM-L6-v2
```
**Solução**: Execute `python download_model.py`

### Erro de dependência
```
ModuleNotFoundError: No module named 'PyQt6'
```
**Solução**: Execute `pip install -r requirements.txt`

### Banco não inicializa
```
✗ Erro ao conectar com banco de dados
```
**Solução**: Verifique permissões na pasta `data/`

### Performance lenta
- Verifique se está usando SSD
- Aumente RAM disponível
- Reduza `similarity_threshold` em `config.py`

## 📝 Logs

Logs são salvos em `data/app.log`. Para debug, edite `config.py`:
```python
LOG_CONFIG = {
    "level": "DEBUG",  # Mude de "INFO"
    # ...
}
```

## 🔒 Segurança

- **Dados locais**: Tudo fica na máquina (SQLite + modelo)
- **Sem rede**: Zero conexões externas após setup
- **Privacidade**: Nenhum dado é enviado para servidores

## 📄 Licença

Este projeto é fornecido como exemplo educacional. Adapte conforme necessário para seu uso corporativo.

## 🤝 Suporte

Para dúvidas sobre implementação:
1. Verifique os logs em `data/app.log`
2. Execute os testes de diagnóstico acima
3. Consulte os comentários no código-fonte