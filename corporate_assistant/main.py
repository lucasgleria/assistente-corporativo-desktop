"""
Assistente Corporativo Desktop - Ponto de entrada principal
Desenvolvido para Windows 10/11 com funcionamento offline
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Adiciona o diretório app ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.models import Base, FAQ, UserFeedback, DynamicPenalty
from app.core.nlp_engine import SearchEngine
from app.ui.tray import SystemTrayManager
from app.ui.chat_controller import ChatController


def create_data_directories():
    """Cria os diretórios necessários para dados e modelo"""
    data_dir = Path("data")
    model_dir = data_dir / "model"
    
    data_dir.mkdir(exist_ok=True)
    model_dir.mkdir(exist_ok=True)
    
    return data_dir, model_dir


def initialize_database():
    """Inicializa o banco de dados e cria as tabelas"""
    try:
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        # Cria todas as tabelas
        Base.metadata.create_all(engine)
        print("✓ Banco de dados inicializado com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}")
        return False


def seed_database():
    """
    Função para popular o banco com dados de exemplo
    Descomente para executar na primeira vez
    """
    # try:
    #     from app.database.repository import FAQRepository
    #     
    #     repo = FAQRepository()
    #     
    #     # Verifica se já existem dados
    #     if repo.count() > 0:
    #         print("✓ Banco já possui dados")
    #         return
    #     
    #     # Dados de exemplo
    #     sample_faqs = [
    #         {
    #             "question": "Como faço para solicitar férias?",
    #             "answer": "Para solicitar férias, acesse o sistema RH interno, vá em 'Solicitações' > 'Férias' e preencha o formulário com as datas desejadas. Lembre-se de solicitar com pelo menos 30 dias de antecedência."
    #         },
    #         {
    #             "question": "Qual é a política de home office da empresa?",
    #             "answer": "A empresa permite home office até 2 dias por semana, mediante aprovação do gestor direto. É necessário ter equipamentos adequados e conexão estável de internet."
    #         },
    #         {
    #             "question": "Como reportar problemas técnicos?",
    #             "answer": "Problemas técnicos devem ser reportados através do sistema de tickets interno ou enviando email para suporte@empresa.com. Inclua sempre uma descrição detalhada do problema."
    #         }
    #     ]
    #     
    #     # Inicializa o engine NLP para gerar embeddings
    #     nlp_engine = SearchEngine()
    #     
    #     for faq_data in sample_faqs:
    #         embedding = nlp_engine.generate_embedding(faq_data["question"])
    #         repo.create(
    #             question=faq_data["question"],
    #             answer=faq_data["answer"],
    #             embedding=embedding
    #         )
    #     
    #     print("✓ Dados de exemplo inseridos com sucesso")
    #     
    # except Exception as e:
    #     print(f"✗ Erro ao popular banco de dados: {e}")
    pass


def main():
    """Função principal da aplicação"""
    # Configurações da aplicação
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Mantém app rodando mesmo com janelas fechadas
    app.setApplicationName("Assistente Corporativo")
    app.setApplicationVersion("1.0.0")
    
    try:
        # Cria diretórios necessários
        data_dir, model_dir = create_data_directories()
        
        # Verifica se o modelo NLP existe (sem bloquear a UI)
        model_path = model_dir / "all-MiniLM-L6-v2"
        if not model_path.exists():
            print("⚠️ Modelo NLP não encontrado - funcionando sem busca semântica")
            print(f"   Caminho esperado: {model_path}")
            print("   Para habilitar busca semântica, baixe o modelo 'all-MiniLM-L6-v2'")
        else:
            print("✓ Modelo NLP encontrado")
        
        # Inicializa o banco de dados
        print("🔄 Inicializando banco de dados...")
        if not initialize_database():
            print("❌ Falha ao inicializar banco de dados - continuando sem persistência")
        else:
            print("✓ Banco de dados inicializado")
        
        # Popula dados de exemplo (descomente se necessário)
        seed_database()
        
        # Inicializa componentes da UI primeiro (sem dependências pesadas)
        print("🎨 Inicializando interface...")
        tray_manager = SystemTrayManager()
        
        # Cria o controlador sem inicializar o modelo ainda
        print("🎮 Criando controlador de chat...")
        chat_controller = ChatController()
        
        # Conecta sinais
        tray_manager.show_chat.connect(chat_controller.open_chat)
        tray_manager.quit_app.connect(app.quit)
        
        # Conecta sinais de estado do chat
        chat_controller.chat_opened.connect(lambda: print("🎉 Chat interface aberta"))
        chat_controller.chat_closed.connect(lambda: print("👋 Chat interface fechada"))
        
        # Mostra componentes iniciais
        tray_manager.show()
        chat_controller.show_components()
        
        print("✓ Assistente Corporativo iniciado com sucesso")
        print("  - Widget flutuante expansível ativo")
        print("  - Ícone na bandeja do sistema")
        print("  - Clique no widget para expandir e abrir o chat")
        print("  - Interface com animações suaves implementada")
        
        return app.exec()
        
    except Exception as e:
        QMessageBox.critical(None, "Erro Fatal", f"Erro ao inicializar aplicação: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())