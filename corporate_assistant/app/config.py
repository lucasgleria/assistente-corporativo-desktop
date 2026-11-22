"""
Configurações e constantes da aplicação
Centralizadas para facilitar manutenção e modificações
"""

import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = DATA_DIR / "model"

# Configurações do Banco de Dados
DATABASE_CONFIG = {
    # SQLite para desenvolvimento/produção inicial
    "sqlite": {
        "url": f"sqlite:///{DATA_DIR}/corporate_assistant.db",
        "echo": False,  # True para debug SQL
        "pool_pre_ping": True
    },
    
    # PostgreSQL para migração futura (apenas alterar a string de conexão)
    "postgresql": {
        "url": "postgresql://user:password@localhost:5432/corporate_assistant",
        "echo": False,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True
    }
}

# Configuração ativa (altere aqui para trocar de banco)
ACTIVE_DB = "sqlite"

# Configurações de Desenvolvimento
DEVELOPMENT_CONFIG = {
    "feedback_enabled": True,  # Habilita sistema de feedback (DESABILITAR EM PRODUÇÃO)
    "show_debug_info": True,   # Mostra informações de debug
    "log_feedback": True,      # Registra feedback no console
    "export_training_data": True  # Permite exportar dados de treinamento
}

# Configurações do Modelo NLP
NLP_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",
    "model_path": MODEL_DIR / "all-MiniLM-L6-v2",
    "similarity_threshold": 0.5,  # Confiança mínima para retornar resposta
    "max_results": 1,  # Número máximo de resultados por busca
    "embedding_dimension": 384  # Dimensão do modelo all-MiniLM-L6-v2
}

# Configurações da Interface
UI_CONFIG = {
    "floating_widget": {
        "size": (100, 100),
        "opacity": 0.8,
        "always_on_top": True,
        # Personalização do botão inicial
        "button": {
            # Opção 1: Usar imagens (prioridade se especificado)
            "image_collapsed": "data/icons/chat.png",  # Caminho para imagem quando colapsado (ex: "data/icons/chat.png")
            "image_expanded": None,   # Caminho para imagem quando expandido (ex: "data/icons/send.png")
            # Se image_collapsed for None, usa icon_collapsed como fallback
            # Opção 2: Usar emoji/texto (fallback se imagem não especificada)
            "icon_collapsed": "",  # Ícone quando colapsado (pode usar emoji ou texto)
            "icon_expanded": "➤",    # Ícone quando expandido
            # Dimensões
            "size": (30, 30),        # Tamanho do botão em pixels (largura, altura)
            "image_size": None,      # Tamanho da imagem (None = usa tamanho do botão)
            "circular_size": 60,     # Tamanho do círculo flutuante em pixels
            "expanded_width": 350,   # Largura quando expandido
            "expanded_height": 50,   # Altura quando expandido
            # Tooltips
            "tooltip_collapsed": "Clique para expandir o chat",
            "tooltip_expanded": "Digite sua pergunta e pressione Enter"
        },
        # Cores do widget flutuante
        "colors": {
            "background_normal": "#1E3A5F",  # Cor de fundo quando normal (azul escuro)
            "background_hover": "#2C5F8D",   # Cor de fundo no hover (azul médio)
            "border_color": "#1E3A5F",       # Cor da borda
            "icon_color": "#FFFFFF",         # Cor do ícone/texto (branco)
            "background_expanded": "#FFFFFF", # Cor de fundo quando expandido
            "border_expanded": "#DEE2E6"     # Cor da borda quando expandido
        },
        # Posicionamento
        "position": {
            "corner": "bottom-right",  # Canto: "bottom-right", "bottom-left", "top-right", "top-left"
            "margin": 20               # Margem do canto em pixels
        }
    },
    "chat_window": {
        "size": (600, 500),
        "min_size": (400, 300),
        "title": "Assistente Corporativo"
    },
    "system_tray": {
        "tooltip": "Assistente Corporativo - Clique para abrir"
    },
    "feedback": {
        "enabled": DEVELOPMENT_CONFIG["feedback_enabled"],  # Controlado por config de desenvolvimento
        "button_size": (20, 20),
        "show_stats": DEVELOPMENT_CONFIG["show_debug_info"],
        "auto_save_embeddings": True
    },
    "colors": {
        # Paleta de cores corporativa profissional
        "primary": "#1E3A5F",      # Azul escuro corporativo
        "secondary": "#2C5F8D",     # Azul médio corporativo
        "accent": "#4A90E2",        # Azul claro para destaques
        "success": "#28A745",       # Verde corporativo
        "warning": "#FFC107",       # Amarelo para avisos
        "danger": "#DC3545",        # Vermelho para erros
        "light": "#F5F7FA",         # Cinza muito claro
        "dark": "#1A1A1A",          # Preto suave
        "white": "#FFFFFF",         # Branco puro
        "text_primary": "#1E3A5F",   # Texto principal (azul escuro)
        "text_secondary": "#6C757D", # Texto secundário (cinza)
        "text_muted": "#ADB5BD",    # Texto desabilitado
        "border": "#DEE2E6",        # Bordas suaves
        "background": "#F8F9FA",    # Fundo principal (cinza muito claro)
        "surface": "#FFFFFF",        # Superfícies (cards, etc)
        "surface_elevated": "#FFFFFF", # Superfícies elevadas
        "user_message": "#2C5F8D",  # Mensagens do usuário (azul corporativo)
        "bot_message": "#FFFFFF",   # Mensagens do bot
        "shadow": "rgba(30, 58, 95, 0.08)", # Sombras sutis
        "shadow_hover": "rgba(30, 58, 95, 0.12)" # Sombras no hover
    },
    "typography": {
        "font_family": "Segoe UI, Arial, sans-serif",
        "font_size_small": "10px",
        "font_size_normal": "12px",
        "font_size_medium": "14px",
        "font_size_large": "16px",
        "font_weight_normal": "400",
        "font_weight_medium": "500",
        "font_weight_bold": "600"
    },
    "spacing": {
        "xxs": "2px",
        "xs": "4px",
        "sm": "6px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
        "xxl": "24px"
    },
    "border_radius": {
        "small": "4px",
        "medium": "8px",
        "large": "12px",
        "circle": "50%"
    }
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    "response_timeout": 1.0,  # Timeout máximo para resposta (segundos)
    "thread_pool_size": 2,  # Número de threads para processamento
    "cache_embeddings": True,  # Cache embeddings em memória
    "batch_size": 100  # Tamanho do batch para operações em lote
}

# Mensagens padrão
DEFAULT_MESSAGES = {
    "welcome": "Olá! Sou seu assistente corporativo. Como posso ajudá-lo hoje?",
    "no_answer": "Desculpe, não encontrei uma resposta para sua pergunta. Tente reformular ou entre em contato com o suporte.",
    "error": "Ocorreu um erro ao processar sua solicitação. Tente novamente.",
    "loading": "Processando sua pergunta..."
}

# Configurações de Log
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": DATA_DIR / "app.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 3
}

def ensure_directories():
    """Garante que todos os diretórios necessários existam"""
    directories = [DATA_DIR, MODEL_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    return True

def get_database_url():
    """Retorna a URL do banco de dados ativo"""
    return DATABASE_CONFIG[ACTIVE_DB]["url"]

def get_database_config():
    """Retorna a configuração completa do banco ativo"""
    return DATABASE_CONFIG[ACTIVE_DB]