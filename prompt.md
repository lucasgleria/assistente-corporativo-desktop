Aqui está o prompt. Eu estruturei ele assumindo o papel de um **Arquiteto de Software Sênior** instruindo um desenvolvedor. Ele é extremamente detalhado para garantir que a IA não "alucine" soluções que dependam da internet ou que criem código espaguete.

Você pode copiar e colar o texto abaixo na sua ferramenta de IA (seja o próprio Gemini, ChatGPT, Claude ou um agente de IDE como o Copilot/Cursor).

-----

### 📋 Prompt Técnico para Geração do Código

**Contexto:**
Atue como um Especialista em Python e Engenharia de Software. Sua tarefa é desenvolver um software desktop para Windows (compatível com Win 10/11) que funcione como um assistente corporativo offline. O software deve ser modular, escalável e seguir os princípios de Clean Code.

**Restrições Críticas:**

1.  **Zero Internet:** O software não pode tentar conectar a APIs externas. O modelo de NLP deve rodar localmente.
2.  **Performance:** Deve rodar em máquinas modestas com resposta \< 1s.
3.  **Banco de Dados:** Deve usar **SQLite** agora, mas a implementação DEVE usar **SQLAlchemy (ORM)** estrito para permitir a troca para PostgreSQL no futuro alterando apenas a string de conexão, sem reescrever queries.
4.  **UI:** Interface moderna usando **PyQt6** ou **PySide6**.

**Stack Tecnológica:**

  * Linguagem: Python 3.10+
  * GUI: PyQt6
  * ORM: SQLAlchemy
  * NLP: `sentence-transformers` (modelo: `all-MiniLM-L6-v2`) + `numpy`.

**Estrutura de Diretórios Obrigatória:**

```text
corporate_assistant/
├── main.py
├── requirements.txt
├── app/
│   ├── config.py (Configurações e constantes)
│   ├── database/ (Camada de dados)
│   │   ├── connection.py (Gerenciamento da Engine/Session)
│   │   ├── models.py (Modelos ORM)
│   │   └── repository.py (CRUD abstrato)
│   ├── core/ (Lógica de Negócio e IA)
│   │   └── nlp_engine.py (Carregamento do modelo e cálculo de similaridade)
│   └── ui/ (Interface Gráfica)
│       ├── tray.py (Ícone na bandeja do sistema)
│       ├── floating_widget.py (A "persona" flutuante estilo Clippy)
│       └── chat_window.py (A janela de chat)
└── data/ (Diretório para o arquivo .db e arquivos do modelo NLP)
```

**Instruções de Implementação por Módulo:**

1.  **Database (`app/database/`):**

      * Crie uma classe `DatabaseManager` em `connection.py` que gerencie a sessão (Singleton).
      * Em `models.py`, crie o modelo `FAQ` com: `id` (Integer, PK), `question` (Text), `answer` (Text), e `embedding` (PickleType ou JSON para armazenar o vetor numpy).
      * *Nota:* Use tipos genéricos do SQLAlchemy para garantir compatibilidade futura com Postgres.

2.  **Core NLP (`app/core/nlp_engine.py`):**

      * Implemente uma classe `SearchEngine`.
      * No método `__init__`, carregue o modelo `sentence-transformers` de um caminho local (`./data/model/`). *Adicione um comentário explicativo sobre como baixar o modelo manualmente para uso offline.*
      * Crie um método `search(query: str, top_k=1)` que:
          * Gera o embedding da pergunta do usuário.
          * Calcula a similaridade de cosseno (Cosine Similarity) usando `numpy` contra os embeddings carregados do banco.
          * Retorna a resposta mais provável se a confiança for \> 0.5 (threshold).

3.  **UI - Floating Widget (`app/ui/floating_widget.py`):**

      * Crie uma pequena janela quadrada (ex: 100x100).
      * **Flags Obrigatórias:** `Qt.WindowType.FramelessWindowHint`, `Qt.WindowType.WindowStaysOnTopHint`, `Qt.WindowType.Tool`.
      * Atributos: Fundo transparente (`WA_TranslucentBackground`). Coloque um placeholder de imagem (um círculo ou ícone).
      * Evento: Ao clicar no widget, emita um sinal para abrir a `ChatWindow`.

4.  **UI - Chat Window (`app/ui/chat_window.py`):**

      * Janela simples com histórico de chat (`QTextEdit` read-only) e campo de entrada (`QLineEdit`).
      * Ao enviar, chame o `SearchEngine` em uma *thread separada* (use `QThread` ou `QRunnable`) para não travar a interface enquanto calcula.

5.  **UI - System Tray (`app/ui/tray.py`):**

      * Deve manter a aplicação rodando mesmo se as janelas forem fechadas.
      * Menu de contexto com opção "Sair" para encerrar o processo completamente.

6.  **Main (`main.py`):**

      * Inicialize o banco de dados (crie as tabelas se não existirem).
      * Inicialize a `QApplication`.
      * Instancie os componentes.
      * Crie uma função "seed" temporária (comentada) para inserir 3 perguntas/respostas de exemplo no banco ao rodar pela primeira vez, gerando seus embeddings.

**Gere o código completo, arquivo por arquivo, focando na robustez e no tratamento de erros.**

-----

### 💡 Dica para você (Usuário)

Quando o agente gerar o código com base nesse prompt, ele provavelmente deixará um comentário do tipo: *"Baixe o modelo e coloque na pasta data"*.

Como você não tem internet na máquina final, você fará o seguinte na **sua máquina de casa**:

1.  Rodará um script Python simples:
    ```python
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save('./meu_projeto/data/model_files')
    ```
2.  Depois, você copiará essa pasta `model_files` junto com o código para o computador da empresa. Isso garante o funcionamento 100% offline que você pediu.