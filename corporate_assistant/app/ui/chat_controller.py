"""
Controlador para coordenar a interação entre FloatingWidget e ChatWindow
Gerencia o fluxo de animações e comunicação entre componentes
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from .floating_widget import FloatingWidget
from .chat_window import ChatWindow


class ChatController(QObject):
    """
    Controlador que coordena a interação entre o widget flutuante e a janela de chat
    """
    
    # Sinais para comunicar com outros componentes
    chat_opened = pyqtSignal()
    chat_closed = pyqtSignal()
    
    def __init__(self):
        """Inicializa o controlador"""
        super().__init__()
        
        # Componentes da UI
        print("🎨 Criando widget flutuante...")
        self.floating_widget = FloatingWidget()
        
        # ChatWindow será criada sob demanda para evitar carregamento lento do modelo
        self.chat_window = None
        
        # Estado
        self.is_chat_open = False
        
        # Timer para auto-fechar o chat se não houver interação
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self._auto_close_chat)
        
        self._connect_signals()
        
        print("✓ Controlador de chat inicializado")
    
    def _ensure_chat_window(self) -> None:
        """Cria a ChatWindow se ainda não existir"""
        if self.chat_window is None:
            print("🎨 Criando janela de chat (carregamento sob demanda)...")
            self.chat_window = ChatWindow()
            
            # Conecta sinais da ChatWindow
            self.chat_window.window_opened.connect(self._on_chat_opened)
            self.chat_window.window_closed.connect(self._on_chat_closed)
            
            print("✓ Janela de chat criada")
    
    def _connect_signals(self) -> None:
        """Conecta os sinais entre os componentes"""
        # Sinais do FloatingWidget
        self.floating_widget.expansion_finished.connect(self._on_widget_expanded)
        self.floating_widget.message_sent.connect(self._on_message_sent)
        self.floating_widget.collapse_finished.connect(self._on_widget_collapsed)
        
        # Sinais da ChatWindow serão conectados quando ela for criada
        
        print("✓ Sinais conectados entre componentes")
    
    def _on_widget_expanded(self) -> None:
        """Callback executado quando o widget termina de expandir"""
        # Garante que a ChatWindow existe
        self._ensure_chat_window()
        
        # NOVO: Não mostra a janela de chat automaticamente
        # A janela só aparecerá após a primeira mensagem ser enviada
        
        # Inicia timer de auto-fechamento (30 segundos sem interação)
        self.auto_close_timer.start(30000)
        
        print("✓ Widget expandido - aguardando primeira mensagem para mostrar chat")
    
    def _on_message_sent(self, message: str) -> None:
        """
        Callback executado quando uma mensagem é enviada
        
        Args:
            message: Mensagem enviada pelo usuário
        """
        # Garante que a ChatWindow existe
        self._ensure_chat_window()
        
        # NOVO: Mostra a janela de chat na primeira mensagem
        if not self.chat_window.is_visible:
            input_geometry = self.floating_widget.get_input_geometry()
            self.chat_window.show_with_growth(input_geometry)
        
        # Processa a mensagem na janela de chat
        self.chat_window.process_message(message)
        
        # Reinicia o timer de auto-fechamento
        self.auto_close_timer.start(30000)
        
        print(f"✓ Mensagem enviada: '{message[:50]}...' - Chat window mostrada")
    
    def _on_widget_collapsed(self) -> None:
        """Callback executado quando o widget termina de colapsar"""
        # Esconde a janela de chat se estiver visível
        if self.chat_window and self.chat_window.is_visible:
            self.chat_window.hide_with_animation()
        
        # Para o timer de auto-fechamento
        self.auto_close_timer.stop()
        
        print("✓ Widget colapsado - escondendo janela de chat")
    
    def _on_chat_opened(self) -> None:
        """Callback executado quando a janela de chat abre"""
        self.is_chat_open = True
        self.chat_opened.emit()
        print("✓ Chat aberto")
    
    def _on_chat_closed(self) -> None:
        """Callback executado quando a janela de chat fecha"""
        self.is_chat_open = False
        
        # Colapsa o widget flutuante
        self.floating_widget.close_input()
        
        # Para o timer de auto-fechamento
        self.auto_close_timer.stop()
        
        self.chat_closed.emit()
        print("✓ Chat fechado")
    
    def _auto_close_chat(self) -> None:
        """Fecha automaticamente o chat após período de inatividade"""
        if self.is_chat_open:
            print("⏰ Auto-fechando chat por inatividade")
            self.close_chat()
    
    def open_chat(self) -> None:
        """Abre o chat (expande o widget)"""
        if not self.floating_widget.is_expanded:
            self.floating_widget.expand_to_input()
    
    def close_chat(self) -> None:
        """Fecha o chat (colapsa o widget)"""
        if self.chat_window and self.chat_window.is_visible:
            self.chat_window.hide_with_animation()
        
        if self.floating_widget.is_expanded:
            self.floating_widget.collapse_to_circle()
    
    def toggle_chat(self) -> None:
        """Alterna o estado do chat"""
        if self.is_chat_open:
            self.close_chat()
        else:
            self.open_chat()
    
    def show_components(self) -> None:
        """Mostra os componentes da UI"""
        self.floating_widget.show()
        print("✓ Componentes da UI exibidos")
    
    def hide_components(self) -> None:
        """Esconde os componentes da UI"""
        self.floating_widget.hide()
        if self.chat_window:
            self.chat_window.hide()
        print("✓ Componentes da UI ocultados")
    
    def cleanup(self) -> None:
        """Limpa recursos do controlador"""
        self.auto_close_timer.stop()
        self.floating_widget.cleanup()
        if self.chat_window:
            self.chat_window.cleanup()
        print("✓ Recursos do controlador limpos")
    
    def get_floating_widget(self) -> FloatingWidget:
        """Retorna referência ao widget flutuante"""
        return self.floating_widget
    
    def get_chat_window(self) -> ChatWindow:
        """Retorna referência à janela de chat (pode ser None)"""
        return self.chat_window