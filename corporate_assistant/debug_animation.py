"""
Script de debug para testar as animações passo a passo
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Adiciona o diretório app ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ui.floating_widget import FloatingWidget
from app.ui.chat_window import ChatWindow

def debug_animations():
    """Testa as animações individualmente"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    print("🔧 Iniciando debug das animações...")
    
    # Cria apenas o widget flutuante primeiro
    widget = FloatingWidget()
    widget.show()
    
    print("✓ Widget flutuante criado e exibido")
    print("  - Clique no círculo roxo para testar a expansão")
    print("  - Pressione Ctrl+C para sair")
    
    # Conecta sinais para debug
    widget.expansion_finished.connect(lambda: print("🎉 DEBUG: Expansão concluída!"))
    widget.collapse_finished.connect(lambda: print("🎉 DEBUG: Colapso concluído!"))
    widget.message_sent.connect(lambda msg: print(f"📨 DEBUG: Mensagem enviada: '{msg}'"))
    
    # Timer para testar automaticamente após 3 segundos
    def auto_test():
        print("🤖 Testando expansão automática...")
        widget.expand_to_input()
    
    QTimer.singleShot(3000, auto_test)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(debug_animations())