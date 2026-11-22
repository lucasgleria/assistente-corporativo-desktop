"""
Janela principal de chat do assistente
Interface para interação com o usuário
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel, QProgressBar,
                            QSplitter, QFrame, QScrollArea, QToolButton, QApplication,
                            QSizePolicy)  # Adicionar QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QTextCursor, QPixmap, QIcon, QPainter, QBrush, QColor
from datetime import datetime
from typing import Optional

from app.config import UI_CONFIG, DEFAULT_MESSAGES
from app.core.nlp_engine import SearchEngine
from app.database.repository import FeedbackRepository
from app.ui.styles import ChatStyles


class SearchWorker(QThread):
    """
    Worker thread para busca semântica
    Evita travamento da interface durante processamento
    """
    
    # Sinais emitidos pelo worker
    search_completed = pyqtSignal(str, float, int)  # (resposta, confiança, faq_id)
    search_failed = pyqtSignal(str)  # (erro)
    
    def __init__(self, query: str):
        """
        Inicializa o worker de busca
        
        Args:
            query: Pergunta do usuário
        """
        super().__init__()
        self.query = query
        self.search_engine = SearchEngine()  # Usa a instância Singleton
        
        print(f"🔍 SearchWorker usando SearchEngine (ID: {id(self.search_engine)})")
    
    def run(self) -> None:
        """Executa a busca em thread separada com aprendizado dinâmico"""
        try:
            print(f"\n🔍 Executando busca: '{self.query}'")
            
            # Debug das penalidades antes da busca
            stats = self.search_engine.get_penalty_stats()
            print(f"📊 Penalidades ativas: {stats.get('total_penalties', 0)}")
            
            # Realiza a busca com aprendizado aplicado
            results = self.search_engine.search(self.query, top_k=1, apply_learning=True)
            
            if results:
                best_result = results[0]
                print(f"✅ Melhor resultado: FAQ #{best_result.faq.id} ({best_result.confidence:.1%})")
                self.search_completed.emit(best_result.answer, best_result.confidence, best_result.faq.id)
            else:
                print("❌ Nenhum resultado encontrado")
                # Sem resultados - não há FAQ para feedback
                self.search_completed.emit(DEFAULT_MESSAGES['no_answer'], 0.0, -1)
                
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            self.search_failed.emit(f"Erro na busca: {str(e)}")


class ChatMessage(QFrame):
    """Widget para exibir uma mensagem individual no chat"""
    
    # Sinais para feedback
    feedback_given = pyqtSignal(str, int, bool, float)  # (user_question, faq_id, is_positive, confidence)
    
    def __init__(self, message: str, is_user: bool = False, confidence: float = 0.0, 
                 faq_id: Optional[int] = None, user_question: str = ""):
        """
        Inicializa uma mensagem do chat
        
        Args:
            message: Texto da mensagem
            is_user: True se for mensagem do usuário
            confidence: Confiança da resposta (0.0 a 1.0)
            faq_id: ID da FAQ (para respostas do bot)
            user_question: Pergunta original do usuário (para feedback)
        """
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.confidence = confidence
        self.faq_id = faq_id
        self.user_question = user_question
        self.feedback_given_flag = False  # Evita feedback duplicado
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura a interface da mensagem"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 2)  # Margens ainda mais reduzidas
        layout.setSpacing(3)  # Espaçamento interno reduzido
        
        # Header com timestamp e confiança
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 2)  # Margem inferior reduzida
        
        # Rótulo do remetente (sem emoji, mais corporativo)
        sender_label = QLabel("Você" if self.is_user else "Assistente")
        sender_font = QFont()
        sender_font.setBold(True)
        sender_font.setPointSize(10)
        sender_label.setFont(sender_font)
        sender_label.setStyleSheet(f"""
            color: {'white' if self.is_user else '#1E3A5F'};
            background: transparent;
            border: none;
        """)
        
        # Timestamp (mais discreto)
        timestamp = datetime.now().strftime("%H:%M")
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: #ADB5BD; font-size: 10px; background: transparent;")
        
        header_layout.addWidget(sender_label)
        header_layout.addStretch()
        
        # Confiança (apenas para respostas do assistente)
        if not self.is_user and self.confidence > 0:
            confidence_text = f"{self.confidence:.0%}"
            confidence_label = QLabel(confidence_text)
            confidence_color = "#28A745" if self.confidence >= 0.7 else "#FFC107" if self.confidence >= 0.5 else "#DC3545"
            confidence_label.setStyleSheet(
                f"color: {confidence_color}; "
                "font-size: 10px; "
                "font-weight: 500; "
                "background: transparent; "
                "padding: 2px 6px; "
                "border-radius: 4px; "
                f"background-color: {confidence_color}15;"
            )
            header_layout.addWidget(confidence_label)
        
        header_layout.addWidget(time_label)
        
        # Mensagem
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Estilo baseado no remetente (margens reduzidas para não cortar)
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2C5F8D;
                    border: none;
                    border-radius: 8px 8px 2px 8px;
                    margin: 2px 8px 2px 4px;
                    padding: 8px 12px;
                    box-shadow: 0 2px 4px rgba(30, 58, 95, 0.1);
                }
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                    font-size: 13px;
                    line-height: 1.4;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #DEE2E6;
                    border-radius: 8px 8px 8px 2px;
                    margin: 2px 4px 2px 8px;
                    padding: 8px 12px;
                    box-shadow: 0 2px 4px rgba(30, 58, 95, 0.08);
                }
                QLabel {
                    color: #1E3A5F;
                    background: transparent;
                    border: none;
                    font-size: 13px;
                    line-height: 1.4;
                }
            """)
        
        layout.addLayout(header_layout)
        layout.addWidget(message_label)
        
        # Botões de feedback (apenas para respostas do assistente)
        if not self.is_user and self.faq_id and UI_CONFIG['feedback']['enabled']:
            self._add_feedback_buttons(layout)
    
    def _add_feedback_buttons(self, layout: QVBoxLayout) -> None:
        """
        Adiciona botões de feedback (thumbs up/down)
        
        Args:
            layout: Layout onde adicionar os botões
        """
        feedback_layout = QHBoxLayout()
        feedback_layout.setContentsMargins(0, 3, 0, 0)  # Margem superior reduzida
        
        # Label de feedback
        feedback_label = QLabel("Útil?")
        feedback_label.setStyleSheet("color: #6C757D; font-size: 10px; background: transparent;")
        
        # Botões de feedback
        self.thumbs_up_btn = QToolButton()
        self.thumbs_up_btn.setText("👍")
        self.thumbs_up_btn.setFixedSize(24, 24)
        self.thumbs_up_btn.setToolTip("Resposta útil")
        self.thumbs_up_btn.setStyleSheet("""
            QToolButton {
                background-color: #F5F7FA;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                color: #6C757D;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #E9ECEF;
                border-color: #2C5F8D;
                color: #2C5F8D;
            }
            QToolButton:pressed {
                background-color: #DEE2E6;
            }
        """)
        self.thumbs_up_btn.clicked.connect(lambda: self._give_feedback(True))
        
        self.thumbs_down_btn = QToolButton()
        self.thumbs_down_btn.setText("👎")
        self.thumbs_down_btn.setFixedSize(24, 24)
        self.thumbs_down_btn.setToolTip("Resposta não útil")
        self.thumbs_down_btn.setStyleSheet("""
            QToolButton {
                background-color: #F5F7FA;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                color: #6C757D;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #E9ECEF;
                border-color: #2C5F8D;
                color: #2C5F8D;
            }
            QToolButton:pressed {
                background-color: #DEE2E6;
            }
        """)
        self.thumbs_down_btn.clicked.connect(lambda: self._give_feedback(False))
        
        # Layout dos botões
        feedback_layout.addWidget(feedback_label)
        feedback_layout.addStretch()
        feedback_layout.addWidget(self.thumbs_up_btn)
        feedback_layout.addWidget(self.thumbs_down_btn)
        
        layout.addLayout(feedback_layout)
    
    def _give_feedback(self, is_positive: bool) -> None:
        """
        Processa feedback do usuário
        
        Args:
            is_positive: True para thumbs up, False para thumbs down
        """
        if self.feedback_given_flag:
            return  # Evita feedback duplicado
        
        self.feedback_given_flag = True
        
        # Emite sinal com dados do feedback
        self.feedback_given.emit(self.user_question, self.faq_id, is_positive, self.confidence)
        
        # Atualiza visual dos botões
        if is_positive:
            self.thumbs_up_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            self.thumbs_down_btn.setEnabled(False)
        else:
            self.thumbs_down_btn.setStyleSheet("background-color: #f44336; color: white;")
            self.thumbs_up_btn.setEnabled(False)
        
        # Mostra confirmação
        feedback_type = "positivo" if is_positive else "negativo"
        print(f"✓ Feedback {feedback_type} registrado para FAQ #{self.faq_id}")


class ChatWindow(QWidget):
    """
    Janela independente do chat que aparece acima do widget flutuante
    """
    
    # Sinais para comunicar mudanças de estado
    window_opened = pyqtSignal()
    window_closed = pyqtSignal()
    
    def __init__(self):
        """Inicializa a janela de chat"""
        super().__init__()
        
        # Configurações da janela (AUMENTADA em 50% verticalmente)
        self.chat_width = 350   # Largura mantida
        self.chat_height = 480  # Altura aumentada em 50% (320 * 1.5 = 480)
        self.window_title = UI_CONFIG['chat_window']['title']
        
        # Estado da animação
        self.is_visible = False
        self.growth_animation = None
        self.input_widget_geometry = None  # Geometria do widget de input
        
        # NOVO: Controle de primeira mensagem
        self.first_message_sent = False
        
        # Componentes
        self.chat_area: QScrollArea = None
        self.chat_container: QWidget = None
        self.chat_layout: QVBoxLayout = None
        self.input_field: QLineEdit = None
        self.send_button: QPushButton = None
        self.progress_bar: QProgressBar = None
        self.status_label: QLabel = None
        
        # Worker thread para busca
        self.search_worker: Optional[SearchWorker] = None
        
        # Engine de busca (Singleton) e repositório de feedback
        self.search_engine = SearchEngine()
        self.feedback_repository = FeedbackRepository()
        
        print(f"🔗 ChatWindow conectado ao SearchEngine (ID: {id(self.search_engine)})")
        
        # Armazena a última pergunta para feedback
        self.last_user_question = ""
        
        self._setup_ui()
        self._setup_animations()
        self._setup_shortcuts()
        self._connect_signals()
        # REMOVIDO: Não adiciona mensagem de boas-vindas automaticamente
    
    def _setup_ui(self) -> None:
        """Configura a interface da janela"""
        # Configurações da janela independente
        self.setWindowTitle(self.window_title)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # Remove bordas
            Qt.WindowType.WindowStaysOnTopHint |     # Sempre no topo
            Qt.WindowType.Tool                       # Não aparece na barra de tarefas
        )
        
        # Atributos da janela
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fundo transparente para bordas arredondadas
        
        # Tamanho fixo da janela
        self.setFixedSize(self.chat_width, self.chat_height)
        
        # Inicialmente oculta
        self.hide()
        
        # Layout principal (OTIMIZADO - margens reduzidas)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(5, 5, 5, 2)  # Margem inferior ainda menor
        
        # Container principal com bordas arredondadas (mais corporativo)
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #DEE2E6;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(30, 58, 95, 0.1);
            }
        """)
        
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(6)  # Espaçamento ainda mais reduzido
        container_layout.setContentsMargins(0, 0, 0, 2)  # Margem inferior mínima
        
        # Header da janela com título e botão fechar
        self._setup_window_header(container_layout)
        
        # Área de chat (scrollable)
        self._setup_chat_area()
        container_layout.addWidget(self.chat_area, 1)  # Expande
        
        # Barra de progresso (inicialmente oculta)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #8A2BE2;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #8A2BE2;
                border-radius: 3px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Botões de aprendizado (apenas se feedback habilitado)
        if UI_CONFIG['feedback']['enabled']:
            self._setup_learning_controls(container_layout)
        
        # Barra de status (OTIMIZADA - mais compacta)
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("color: gray; font-size: 10px; padding: 1px; margin: 0px;")
        self.status_label.setMaximumHeight(15)  # Altura máxima reduzida
        container_layout.addWidget(self.status_label)
        
        # Adiciona o container principal ao layout
        main_layout.addWidget(main_container)
        
        print("✓ Interface do chat configurada")
    
    def _setup_window_header(self, container_layout: QVBoxLayout) -> None:
        """
        Configura o cabeçalho da janela com título e botão fechar
        """
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E3A5F, 
                    stop:1 #2C5F8D);
                border: none;
                border-radius: 12px 12px 0px 0px;
                padding: 0px;
            }
        """)
        header_frame.setFixedHeight(45)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 12, 12)
        header_layout.setSpacing(12)
        
        # Título da janela (mais corporativo)
        title_label = QLabel("Assistente Corporativo")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 600;
                font-size: 14px;
                background: transparent;
                border: none;
                letter-spacing: 0.3px;
            }
        """)
        
        # Botão fechar (mais elegante)
        close_button = QPushButton("×")
        close_button.setFixedSize(28, 28)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                color: white;
                font-weight: 500;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        close_button.setToolTip("Fechar")
        close_button.clicked.connect(self.hide_with_animation)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        container_layout.addWidget(header_frame)
    
    def _setup_animations(self) -> None:
        """Configura as animações da janela"""
        # Animação de crescimento vertical
        self.growth_animation = QPropertyAnimation(self, b"geometry")
        self.growth_animation.setDuration(400)  # 400ms para animação suave
        self.growth_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        print("✓ Animações configuradas")
    
    def _setup_shortcuts(self) -> None:
        """Configura atalhos de teclado"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Esc para fechar a janela
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.hide_with_animation)
        
        print("✓ Atalhos de teclado configurados")
    
    def update_position(self, input_geometry: QRect) -> None:
        """
        Atualiza a posição da janela baseada na geometria do widget de input
        
        Args:
            input_geometry: Geometria do widget de input
        """
        self.input_widget_geometry = input_geometry
        
        # CORREÇÃO: Posicionamento para crescer para cima do input
        margin = 5  # Margem menor para ficar mais próximo
        
        # Alinhamento X: Borda direita da janela alinhada com borda direita do input
        x = input_geometry.right() - self.chat_width
        
        # CORREÇÃO CRÍTICA: Posiciona a janela para que ela termine exatamente acima do input
        # A janela deve crescer para cima a partir desta posição
        y = input_geometry.top() - self.chat_height - margin
        
        # Garante que a janela não saia da tela
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Ajusta X se sair da tela pela esquerda
        if x < screen_geometry.x():
            x = screen_geometry.x() + 10
        # Ajusta X se sair da tela pela direita  
        elif x + self.chat_width > screen_geometry.right():
            x = screen_geometry.right() - self.chat_width - 10
        
        # CORREÇÃO: Verifica se cabe acima do input
        if y < screen_geometry.y():
            # Se não couber acima, reduz a altura da janela ou posiciona no topo da tela
            available_height = input_geometry.top() - screen_geometry.y() - margin
            if available_height > 200:  # Altura mínima aceitável
                self.chat_height = min(self.chat_height, available_height)
                y = screen_geometry.y() + 10
            else:
                # Se não couber acima, posiciona abaixo do input
                y = input_geometry.bottom() + margin
        
        self.move(x, y)
        print(f"📍 ChatWindow posicionada em ({x}, {y}) - Input: {input_geometry}")
        print(f"📏 Altura da janela: {self.chat_height}px")
    
    def _get_growth_start_position(self) -> QRect:
        """Calcula a posição inicial da animação (altura zero)"""
        # CORREÇÃO CRÍTICA: Para crescer PARA CIMA do input:
        # 1. A janela deve começar onde ficará o fundo (próximo ao input)
        # 2. Com altura zero
        # 3. E crescer para cima até a posição final
        
        # Posição onde ficará o fundo da janela (próximo ao input)
        if self.input_widget_geometry:
            # Fundo da janela fica próximo ao topo do input
            bottom_y = self.input_widget_geometry.top() - 5
            start_y = bottom_y  # Começa do fundo com altura zero
        else:
            # Fallback se não tiver geometria do input
            current_pos = self.pos()
            start_y = current_pos.y() + self.chat_height
        
        return QRect(self.pos().x(), start_y, self.chat_width, 0)
    
    def _get_growth_end_position(self) -> QRect:
        """Calcula a posição final da animação (altura completa)"""
        # CORREÇÃO: A posição final deve ser calculada para que o fundo
        # da janela fique próximo ao input e ela cresça para cima
        
        if self.input_widget_geometry:
            # Fundo da janela fica próximo ao topo do input
            bottom_y = self.input_widget_geometry.top() - 5
            # Topo da janela fica na altura completa acima do fundo
            top_y = bottom_y - self.chat_height
            return QRect(self.pos().x(), top_y, self.chat_width, self.chat_height)
        else:
            # Fallback
            current_pos = self.pos()
            return QRect(current_pos.x(), current_pos.y(), self.chat_width, self.chat_height)
    
    def _setup_learning_controls(self, main_layout: QVBoxLayout) -> None:
        """
        Configura os controles de aprendizado (salvar/carregar)
        
        Args:
            main_layout: Layout principal onde adicionar os controles
        """
        # Frame para controles de aprendizado
        learning_frame = QFrame()
        learning_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 1px solid #b0c4de;
                border-radius: 5px;
                margin: 1px;
                padding: 3px;
            }
        """)
        
        learning_layout = QHBoxLayout(learning_frame)
        learning_layout.setContentsMargins(4, 2, 4, 2)  # Margens ainda mais reduzidas
        
        # Label (OTIMIZADO - menor)
        learning_label = QLabel("🧠")
        learning_label.setStyleSheet("font-weight: bold; color: #4682b4; font-size: 11px;")
        learning_label.setToolTip("Controles de Aprendizado")
        
        # Botões OTIMIZADOS - ainda menores e mais compactos
        self.save_learning_btn = QPushButton("💾")
        self.save_learning_btn.setToolTip("Salvar aprendizado")
        self.save_learning_btn.setFixedSize(22, 22)
        self.save_learning_btn.clicked.connect(self._save_learning)
        
        self.load_learning_btn = QPushButton("📂")
        self.load_learning_btn.setToolTip("Carregar aprendizado")
        self.load_learning_btn.setFixedSize(22, 22)
        self.load_learning_btn.clicked.connect(self._load_learning)
        
        self.clear_learning_btn = QPushButton("🧹")
        self.clear_learning_btn.setToolTip("Limpar aprendizado")
        self.clear_learning_btn.setFixedSize(22, 22)
        self.clear_learning_btn.clicked.connect(self._clear_learning)
        
        self.info_learning_btn = QPushButton("ℹ️")
        self.info_learning_btn.setToolTip("Informações do aprendizado")
        self.info_learning_btn.setFixedSize(22, 22)
        self.info_learning_btn.clicked.connect(self._show_learning_info)
        
        # Layout
        learning_layout.addWidget(learning_label)
        learning_layout.addStretch()
        learning_layout.addWidget(self.save_learning_btn)
        learning_layout.addWidget(self.load_learning_btn)
        learning_layout.addWidget(self.clear_learning_btn)
        learning_layout.addWidget(self.info_learning_btn)
        
        main_layout.addWidget(learning_frame)
        
        print("✓ Controles de aprendizado configurados")
    
    def _setup_chat_area(self) -> None:
        """Configura a área scrollable do chat"""
        # Container para as mensagens
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(6)  # Espaçamento reduzido entre mensagens
        self.chat_layout.setContentsMargins(8, 8, 8, 0)  # Margem inferior removida
        
        # Área scrollable
        self.chat_area = QScrollArea()
        self.chat_area.setWidget(self.chat_container)
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # CORREÇÃO: Configura o container para ter altura mínima baseada no conteúdo
        self.chat_container.setMinimumHeight(0)
        self.chat_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Minimum  # Altura mínima baseada no conteúdo
        )
        
        # CORREÇÃO: Remove bordas e adiciona estilo corporativo
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)
        self.chat_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8F9FA;
            }
            QScrollBar:vertical {
                background-color: #F5F7FA;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #DEE2E6;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2C5F8D;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
    
    def _connect_signals(self) -> None:
        """Conecta os sinais da interface"""
        # Não há mais input field nesta janela - o input está no FloatingWidget
        pass
    
    def _add_welcome_message(self) -> None:
        """Adiciona mensagem de boas-vindas"""
        welcome_msg = DEFAULT_MESSAGES['welcome']
        
        # Adiciona informação sobre disponibilidade do modelo
        if not self.search_engine.is_available():
            welcome_msg += "\n\n⚠️ Nota: O modelo de busca semântica não está disponível. " \
                          "Algumas funcionalidades podem estar limitadas."
        
        # Adiciona informação sobre feedback se habilitado
        if UI_CONFIG['feedback']['enabled']:
            welcome_msg += "\n\n💡 Dica: Use os botões 👍👎 para avaliar as respostas e ajudar a melhorar o sistema!"
        
        self._add_message(welcome_msg, is_user=False)
    
    def process_message(self, user_message: str) -> None:
        """
        Processa mensagem recebida do widget flutuante
        
        Args:
            user_message: Mensagem do usuário
        """
        if not user_message.strip():
            return
        
        # NOVO: Se é a primeira mensagem, adiciona boas-vindas primeiro
        if not self.first_message_sent:
            self._add_welcome_message()
            self.first_message_sent = True
        
        # Armazena pergunta para feedback posterior
        self.last_user_question = user_message
        
        # Adiciona mensagem do usuário
        self._add_message(user_message, is_user=True)
        
        # Desabilita interface durante processamento
        self._set_processing_state(True)
        
        # Inicia busca em thread separada
        self._start_search(user_message)
    
    def _start_search(self, query: str) -> None:
        """
        Inicia busca semântica em thread separada
        
        Args:
            query: Pergunta do usuário
        """
        # Para worker anterior se estiver rodando
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        # Cria novo worker
        self.search_worker = SearchWorker(query)
        self.search_worker.search_completed.connect(self._on_search_completed)
        self.search_worker.search_failed.connect(self._on_search_failed)
        self.search_worker.finished.connect(lambda: self._set_processing_state(False))
        
        # Inicia busca
        self.search_worker.start()
    
    def _on_search_completed(self, answer: str, confidence: float, faq_id: int) -> None:
        """
        Manipula conclusão da busca
        
        Args:
            answer: Resposta encontrada
            confidence: Confiança da resposta
            faq_id: ID da FAQ encontrada (-1 se não encontrou)
        """
        # Adiciona mensagem com dados para feedback
        self._add_message(
            answer, 
            is_user=False, 
            confidence=confidence,
            faq_id=faq_id if faq_id != -1 else None,
            user_question=self.last_user_question
        )
    
    def _on_search_failed(self, error: str) -> None:
        """
        Manipula falha na busca
        
        Args:
            error: Mensagem de erro
        """
        error_msg = f"{DEFAULT_MESSAGES['error']}\n\nDetalhes: {error}"
        self._add_message(error_msg, is_user=False)
    
    def _add_message(self, message: str, is_user: bool = False, confidence: float = 0.0,
                    faq_id: Optional[int] = None, user_question: str = "") -> None:
        """
        Adiciona uma mensagem ao chat
        
        Args:
            message: Texto da mensagem
            is_user: True se for mensagem do usuário
            confidence: Confiança da resposta (para mensagens do assistente)
            faq_id: ID da FAQ (para feedback)
            user_question: Pergunta original do usuário (para feedback)
        """
        # Cria widget da mensagem
        message_widget = ChatMessage(message, is_user, confidence, faq_id, user_question)
        
        # Conecta sinal de feedback se for resposta do bot
        if not is_user and faq_id:
            message_widget.feedback_given.connect(self._handle_feedback)
        
        # CORREÇÃO: Remove qualquer stretch existente antes de adicionar nova mensagem
        # Isso evita espaço extra no final
        while self.chat_layout.count() > 0:
            item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if item and item.spacerItem():
                self.chat_layout.removeItem(item)
            else:
                break  # Para quando encontrar um widget
        
        # Adiciona ao layout
        self.chat_layout.addWidget(message_widget)
        
        # Scroll para o final
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _handle_feedback(self, user_question: str, faq_id: int, is_positive: bool, confidence: float) -> None:
        """
        Processa feedback do usuário com aprendizado em tempo real
        
        Args:
            user_question: Pergunta original do usuário
            faq_id: ID da FAQ avaliada
            is_positive: True para thumbs up, False para thumbs down
            confidence: Confiança da resposta
        """
        try:
            # Gera embedding da pergunta se possível
            user_embedding = None
            if self.search_engine.is_available():
                user_embedding = self.search_engine.generate_embedding(user_question)
            
            # Salva feedback no banco
            feedback = self.feedback_repository.create_feedback(
                user_question=user_question,
                faq_id=faq_id,
                is_positive=is_positive,
                confidence_score=confidence,
                user_question_embedding=user_embedding
            )
            
            # APRENDIZADO EM TEMPO REAL: Aplica penalidade se feedback negativo
            if not is_positive:
                print(f"\n🎯 Aplicando aprendizado para FAQ #{faq_id}")
                print(f"   Pergunta: '{user_question}'")
                
                learning_success = self.search_engine.apply_negative_feedback(
                    user_question=user_question,
                    faq_id=faq_id,
                    penalty_factor=0.4  # Reduz score em 60% (menos agressivo)
                )
                
                if learning_success:
                    # Debug das penalidades após aplicar
                    self.search_engine.debug_penalties(user_question)
                    feedback_message = "👎 Entendi! Não vou sugerir esta resposta para perguntas similares."
                else:
                    feedback_message = "👎 Obrigado pelo feedback! Vamos melhorar esta resposta."
            else:
                feedback_message = "👍 Obrigado pelo feedback positivo!"
            
            # Mostra confirmação visual
            self.status_label.setText(feedback_message)
            
            # Volta ao status normal após 4 segundos (mais tempo para ler a mensagem de aprendizado)
            QTimer.singleShot(4000, lambda: self.status_label.setText("Pronto"))
            
            # Log detalhado para desenvolvimento
            learning_status = "com aprendizado aplicado" if not is_positive else "registrado"
            print(f"✓ Feedback {learning_status}: ID={feedback.id}, Positivo={is_positive}, FAQ={faq_id}")
            
        except Exception as e:
            print(f"✗ Erro ao processar feedback: {e}")
            self.status_label.setText("Erro ao processar feedback")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
    
    def _scroll_to_bottom(self) -> None:
        """Faz scroll para a última mensagem"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _set_processing_state(self, processing: bool) -> None:
        """
        Define o estado de processamento da interface
        
        Args:
            processing: True se estiver processando
        """
        # Mostra/esconde barra de progresso
        self.progress_bar.setVisible(processing)
        if processing:
            self.progress_bar.setRange(0, 0)  # Indeterminado
        
        # Atualiza status
        if processing:
            self.status_label.setText(DEFAULT_MESSAGES['loading'])
        else:
            self.status_label.setText("Pronto")
    
    def show_with_growth(self, input_geometry: QRect) -> None:
        """
        Mostra a janela com animação de crescimento vertical
        
        Args:
            input_geometry: Geometria do widget de input para posicionamento
        """
        if self.is_visible:
            # Se já está visível, apenas dá foco
            self.raise_()
            self.activateWindow()
            return
        
        # Atualiza posição baseada no widget de input
        self.update_position(input_geometry)
        
        # Configura geometria inicial (altura zero)
        start_geometry = self._get_growth_start_position()
        self.setGeometry(start_geometry)
        
        # Mostra a janela
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Inicia animação de crescimento
        self.growth_animation.setStartValue(start_geometry)
        self.growth_animation.setEndValue(self._get_growth_end_position())
        self.growth_animation.finished.connect(self._on_growth_finished)
        self.growth_animation.start()
        
        self.is_visible = True
        print("🎬 Iniciando animação de crescimento da janela")
    
    def _on_growth_finished(self) -> None:
        """Callback executado quando a animação de crescimento termina"""
        self.growth_animation.finished.disconnect()
        self.window_opened.emit()  # Emite sinal de janela aberta
        print("✓ Janela cresceu completamente")
    
    def hide_with_animation(self) -> None:
        """Esconde a janela com animação de encolhimento"""
        if not self.is_visible:
            return
        
        # Inicia animação de encolhimento
        self.growth_animation.setStartValue(self.geometry())
        self.growth_animation.setEndValue(self._get_growth_start_position())
        self.growth_animation.finished.connect(self._on_shrink_finished)
        self.growth_animation.start()
        
        print("🎬 Iniciando animação de encolhimento da janela")
    
    def _on_shrink_finished(self) -> None:
        """Callback executado quando a animação de encolhimento termina"""
        self.growth_animation.finished.disconnect()
        self.hide()
        self.is_visible = False
        self.window_closed.emit()  # Emite sinal de janela fechada
        print("✓ Janela encolhida e ocultada")
    
    def clear_chat(self) -> None:
        """Limpa o histórico do chat"""
        # Remove todas as mensagens
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Adiciona mensagem de boas-vindas novamente
        self._add_welcome_message()
    
    def closeEvent(self, event) -> None:
        """
        Manipula fechamento da janela
        
        Args:
            event: Evento de fechamento
        """
        # Para worker se estiver rodando
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        # Esconde com animação ao invés de fechar
        event.ignore()
        self.hide_with_animation()
    
    def _save_learning(self) -> None:
        """Salva o aprendizado atual"""
        try:
            success = self.search_engine.save_learning_to_file()
            
            if success:
                self.status_label.setText("💾 Aprendizado salvo com sucesso!")
                self._add_system_message("💾 Aprendizado salvo! Será restaurado na próxima sessão.")
            else:
                self.status_label.setText("❌ Erro ao salvar aprendizado")
                self._add_system_message("❌ Erro ao salvar aprendizado. Verifique os logs.")
            
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
            
        except Exception as e:
            print(f"❌ Erro ao salvar aprendizado: {e}")
            self.status_label.setText("❌ Erro ao salvar")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
    
    def _load_learning(self) -> None:
        """Carrega aprendizado salvo"""
        try:
            success = self.search_engine.load_learning_from_file()
            
            if success:
                stats = self.search_engine.get_penalty_stats()
                self.status_label.setText("📂 Aprendizado carregado com sucesso!")
                self._add_system_message(
                    f"📂 Aprendizado carregado! "
                    f"{stats.get('total_penalties', 0)} penalidades restauradas."
                )
            else:
                self.status_label.setText("ℹ️ Nenhum aprendizado salvo encontrado")
                self._add_system_message("ℹ️ Nenhum arquivo de aprendizado encontrado.")
            
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
            
        except Exception as e:
            print(f"❌ Erro ao carregar aprendizado: {e}")
            self.status_label.setText("❌ Erro ao carregar")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
    
    def _clear_learning(self) -> None:
        """Limpa todo o aprendizado atual"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # Confirma a ação
            reply = QMessageBox.question(
                self,
                "Confirmar Limpeza",
                "Tem certeza que deseja limpar todo o aprendizado atual?\n\n"
                "Esta ação não pode ser desfeita.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.search_engine.clear_penalties()
                self.status_label.setText("🧹 Aprendizado limpo!")
                self._add_system_message("🧹 Todo o aprendizado foi removido.")
                
                QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
            
        except Exception as e:
            print(f"❌ Erro ao limpar aprendizado: {e}")
            self.status_label.setText("❌ Erro ao limpar")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
    
    def _show_learning_info(self) -> None:
        """Mostra informações sobre o aprendizado"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # Estatísticas do aprendizado atual
            stats = self.search_engine.get_penalty_stats()
            
            # Informações do arquivo
            file_info = self.search_engine.get_learning_file_info()
            
            # Monta mensagem
            info_text = "<h3>📊 Informações do Aprendizado</h3>"
            
            info_text += "<h4>🧠 Aprendizado Atual (Memória):</h4>"
            info_text += f"• Total de penalidades: <b>{stats.get('total_penalties', 0)}</b><br>"
            info_text += f"• FAQs penalizadas: <b>{stats.get('penalized_faqs', 0)}</b><br>"
            info_text += f"• Sistema: <b>{stats.get('system_type', 'unknown')}</b><br>"
            
            if stats.get('penalties_detail'):
                info_text += "<br><b>Detalhes por FAQ:</b><br>"
                for faq_id, count in stats.get('penalties_detail', {}).items():
                    info_text += f"  • FAQ #{faq_id}: {count} penalidades<br>"
            
            info_text += "<h4>💾 Arquivo Salvo:</h4>"
            if file_info.get('exists'):
                info_text += f"• Arquivo: <b>Existe</b><br>"
                info_text += f"• Tamanho: <b>{file_info.get('size_mb', 0)} MB</b><br>"
                info_text += f"• Modificado: <b>{file_info.get('modified', 'N/A')}</b><br>"
                info_text += f"• Caminho: <code>{file_info.get('filepath', 'N/A')}</code><br>"
            else:
                info_text += "• <b>Nenhum arquivo salvo encontrado</b><br>"
            
            info_text += "<br><i>💡 Dica: Use 'Salvar' para preservar o aprendizado entre sessões!</i>"
            
            QMessageBox.information(self, "Informações do Aprendizado", info_text)
            
        except Exception as e:
            print(f"❌ Erro ao mostrar informações: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao obter informações: {e}")
    
    def _add_system_message(self, message: str) -> None:
        """
        Adiciona uma mensagem do sistema ao chat
        
        Args:
            message: Mensagem do sistema
        """
        system_message = f"🤖 Sistema: {message}"
        self._add_message(system_message, is_user=False, confidence=1.0)
    
    def toggle_visibility(self, input_geometry: QRect = None) -> None:
        """
        Alterna a visibilidade da janela com animação
        
        Args:
            input_geometry: Geometria do widget de input (necessária para mostrar)
        """
        if self.is_visible:
            self.hide_with_animation()
        else:
            if input_geometry:
                self.show_with_growth(input_geometry)
            else:
                print("⚠ Geometria do input necessária para mostrar a janela")
    
    def cleanup(self) -> None:
        """Limpa recursos da janela"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        if self.growth_animation:
            self.growth_animation.stop()
        
        print("✓ Recursos da janela de chat limpos")