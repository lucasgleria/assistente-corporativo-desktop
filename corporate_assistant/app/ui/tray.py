"""
Gerenciador do ícone na bandeja do sistema (System Tray)
Mantém a aplicação rodando em background
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
import sys

from app.config import UI_CONFIG


class SystemTrayManager(QObject):
    """
    Gerenciador do ícone na bandeja do sistema
    Permite controlar a aplicação mesmo com janelas fechadas
    """
    
    # Sinais emitidos pelo tray
    show_chat = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(self):
        """Inicializa o gerenciador da bandeja"""
        super().__init__()
        
        self.tray_icon: QSystemTrayIcon = None
        self.tray_menu: QMenu = None
        
        # Configurações
        self.tooltip = UI_CONFIG['system_tray']['tooltip']
        
        self._create_tray_icon()
        self._create_tray_menu()
        self._connect_signals()
    
    def _create_tray_icon(self) -> None:
        """Cria o ícone da bandeja do sistema"""
        try:
            # Cria um ícone simples programaticamente (círculo azul)
            icon = self._create_default_icon()
            
            # Cria o ícone da bandeja
            self.tray_icon = QSystemTrayIcon(icon)
            self.tray_icon.setToolTip(self.tooltip)
            
            print("✓ Ícone da bandeja criado")
            
        except Exception as e:
            print(f"✗ Erro ao criar ícone da bandeja: {e}")
    
    def _create_default_icon(self) -> QIcon:
        """
        Cria um ícone padrão programaticamente
        
        Returns:
            QIcon com um círculo azul simples
        """
        # Cria um pixmap 32x32
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparente
        
        # Desenha um círculo azul
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(70, 130, 180)))  # Azul aço
        painter.setPen(QColor(50, 100, 150))
        painter.drawEllipse(2, 2, 28, 28)
        
        # Desenha um "A" no centro (Assistente)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), 0x84, "A")  # AlignCenter | AlignVCenter
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_tray_menu(self) -> None:
        """Cria o menu de contexto da bandeja"""
        try:
            self.tray_menu = QMenu()
            
            # Ação: Abrir Chat
            show_action = self.tray_menu.addAction("🗨️ Abrir Chat")
            show_action.triggered.connect(self.show_chat.emit)
            
            # Separador
            self.tray_menu.addSeparator()
            
            # Ação: Sobre
            about_action = self.tray_menu.addAction("ℹ️ Sobre")
            about_action.triggered.connect(self._show_about)
            
            # Separador
            self.tray_menu.addSeparator()
            
            # Ação: Sair
            quit_action = self.tray_menu.addAction("❌ Sair")
            quit_action.triggered.connect(self.quit_app.emit)
            
            # Associa o menu ao ícone
            self.tray_icon.setContextMenu(self.tray_menu)
            
            print("✓ Menu da bandeja criado")
            
        except Exception as e:
            print(f"✗ Erro ao criar menu da bandeja: {e}")
    
    def _connect_signals(self) -> None:
        """Conecta os sinais do ícone da bandeja"""
        if self.tray_icon:
            # Clique duplo abre o chat
            self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Manipula cliques no ícone da bandeja
        
        Args:
            reason: Tipo de ativação (clique, duplo clique, etc.)
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_chat.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Clique simples também abre (mais intuitivo)
            self.show_chat.emit()
    
    def _show_about(self) -> None:
        """Mostra informações sobre a aplicação"""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            None,
            "Sobre - Assistente Corporativo",
            "<h3>Assistente Corporativo</h3>"
            "<p><b>Versão:</b> 1.0.0</p>"
            "<p><b>Descrição:</b> Assistente offline para perguntas corporativas</p>"
            "<p><b>Tecnologias:</b> Python, PyQt6, SQLAlchemy, Sentence Transformers</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Busca semântica offline</li>"
            "<li>Interface flutuante</li>"
            "<li>Banco de dados local</li>"
            "</ul>"
            "<p><i>Desenvolvido para Windows 10/11</i></p>"
        )
    
    def show(self) -> None:
        """Mostra o ícone na bandeja"""
        if self.tray_icon and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            print("✓ Ícone da bandeja ativado")
        else:
            print("⚠ Bandeja do sistema não disponível")
    
    def hide(self) -> None:
        """Esconde o ícone da bandeja"""
        if self.tray_icon:
            self.tray_icon.hide()
            print("ℹ Ícone da bandeja ocultado")
    
    def show_message(self, title: str, message: str, 
                    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                    timeout: int = 3000) -> None:
        """
        Mostra uma notificação na bandeja
        
        Args:
            title: Título da notificação
            message: Mensagem da notificação
            icon: Tipo de ícone da notificação
            timeout: Tempo em milissegundos para auto-fechar
        """
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)
    
    def is_available(self) -> bool:
        """
        Verifica se a bandeja do sistema está disponível
        
        Returns:
            True se a bandeja estiver disponível
        """
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    def is_visible(self) -> bool:
        """
        Verifica se o ícone está visível na bandeja
        
        Returns:
            True se o ícone estiver visível
        """
        return self.tray_icon and self.tray_icon.isVisible()
    
    def update_tooltip(self, tooltip: str) -> None:
        """
        Atualiza o tooltip do ícone
        
        Args:
            tooltip: Novo texto do tooltip
        """
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
    
    def cleanup(self) -> None:
        """Limpa recursos da bandeja"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
        
        if self.tray_menu:
            self.tray_menu.clear()
            self.tray_menu = None
        
        print("✓ Recursos da bandeja limpos")