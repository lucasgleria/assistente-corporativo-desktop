# 🚀 Guia de Início Rápido

## Instalação em 3 Passos

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Baixar Modelo NLP
```bash
python download_model.py
```

### 3️⃣ Adicionar Dados de Exemplo
```bash
python add_sample_data.py
```

## ▶️ Executar

### Opção 1: Python
```bash
python main.py
```

### Opção 2: Windows (Duplo clique)
```
run.bat
```

## 🧪 Testar Sistema
```bash
python test_system.py
```

## 💡 Uso Básico

1. **Widget Flutuante**: Aparece no canto da tela
2. **Clique no Widget**: Abre janela de chat
3. **Digite Perguntas**: Como "Como solicitar férias?"
4. **Receba Respostas**: Instantâneas e inteligentes
5. **Avalie Respostas**: Use 👍👎 para melhorar o sistema

## 🔧 Solução Rápida de Problemas

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Modelo não encontrado | `python download_model.py` |
| Sem respostas | `python add_sample_data.py` |
| Erro geral | `python test_system.py` |

## 📝 Personalização

### Adicionar Suas Próprias Perguntas
1. Edite `add_sample_data.py`
2. Modifique a lista `sample_faqs`
3. Execute novamente o script

### Mudar Configurações
- Edite `app/config.py`
- Ajuste threshold, cores, tamanhos, etc.

## 🎯 Funcionalidades

- ✅ **Busca Semântica**: Entende sinônimos e contexto
- ✅ **100% Offline**: Funciona sem internet
- ✅ **Interface Moderna**: Widget flutuante + chat
- ✅ **Sistema Tray**: Sempre disponível
- ✅ **Performance**: Resposta < 1 segundo
- ✅ **Escalável**: SQLite → PostgreSQL fácil
- ✅ **Sistema de Feedback**: Botões 👍👎 para treinar (desenvolvimento)

## 📞 Suporte

1. Execute `python test_system.py` para diagnóstico
2. Verifique logs em `data/app.log`
3. Analise feedback: `python view_feedback_stats.py`
4. Consulte `README.md` para detalhes completos

## 🚀 Para Produção

Quando estiver satisfeito com o treinamento:
```bash
python disable_feedback.py
```
Remove o sistema de feedback e prepara para distribuição final.



---



🚀 Como Usar
Durante Desenvolvimento:

# 1. Execute o assistente
python main.py

# 2. Use normalmente e clique 👍👎 nas respostas

# 3. Analise os dados coletados
python view_feedback_stats.py

# 4. Veja demonstração
python demo_feedback.py
Para Produção:

# Remove sistema de feedback completamente
python disable_feedback.py