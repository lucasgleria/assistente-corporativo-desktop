"""
Versão simplificada do main.py para teste
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Adiciona o diretório app ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ui.chat_controller import ChatController

def main_simple():
    """Versão simplificada da função principal"""
    # Configurações da aplicação
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Assistente Corporativo - Teste")
    app.setApplicationVersion("1.0.0")
    
    try:
        print("🚀 Iniciando versão simplificada...")
        
        # Inicializa apenas o controlador de chat
        chat_controller = ChatController()
        
        # Mostra componentes
        chat_controller.show_components()
        
        print("✓ Assistente Corporativo (versão simplificada) iniciado com sucesso")
        print("  - Widget flutuante expansível ativo")
        print("  - Clique no widget roxo para expandir e abrir o chat")
        print("  - Digite uma mensagem para testar")
        print("  - Pressione Ctrl+C para sair")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main_simple())