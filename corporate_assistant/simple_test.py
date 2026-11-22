"""
Teste simples da nova interface
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

# Adiciona o diretório app ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def simple_test():
    """Teste básico da PyQt6"""
    app = QApplication(sys.argv)
    
    # Janela de teste simples
    window = QWidget()
    window.setWindowTitle("Teste Simples")
    window.setGeometry(100, 100, 300, 200)
    
    layout = QVBoxLayout()
    
    button = QPushButton("Teste - Clique aqui")
    button.clicked.connect(lambda: print("✓ Botão funcionando!"))
    
    layout.addWidget(button)
    window.setLayout(layout)
    
    window.show()
    
    print("✓ Teste simples iniciado")
    print("  - Clique no botão para testar")
    print("  - Feche a janela para sair")
    
    # Auto-fechar após 5 segundos
    QTimer.singleShot(5000, app.quit)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(simple_test())