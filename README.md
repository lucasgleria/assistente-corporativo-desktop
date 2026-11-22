# Assistente Corporativo Desktop

Protótipo de assistente corporativo **offline** para Windows: um widget flutuante e uma janela de chat que respondem perguntas internas (férias, home office, reembolso, TI…) por **busca semântica local**, sem internet.

- **Stack:** Python 3.10+, PyQt6, SQLAlchemy (SQLite, pronto para PostgreSQL), sentence-transformers (`all-MiniLM-L6-v2`).
- **Recursos:** ícone na bandeja, widget flutuante, chat, feedback 👍/👎 para ajustar respostas.
- **Status:** protótipo (dez/2025).

O código e as instruções completas estão em [`corporate_assistant/`](corporate_assistant/README.md). Em resumo:

```bash
cd corporate_assistant
pip install -r requirements.txt
python download_model.py      # baixa o modelo NLP (~90 MB)
python add_sample_data.py     # perguntas de exemplo
python main.py
```

[`prompt.md`](prompt.md) é o prompt de arquitetura usado para gerar a estrutura inicial do projeto com IA.
