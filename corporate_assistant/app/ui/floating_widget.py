"""
Widget flutuante expansível
Botão circular que se expande em barra de input com animações suaves
"""

from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, 
                         QParallelAnimationGroup, QSequentialAnimationGroup, QRect, QSize)
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QCursor, QIcon, QPixmap
import math
from pathlib import Path

from app.config import UI_CONFIG, BASE_DIR


class FloatingWidget(QWidget):
    """
    Widget flutuante expansível que transforma de círculo em barra de input
    """
    
    # Sinais emitidos pelo widget
    message_sent = pyqtSignal(str)  # Quando uma mensagem é enviada
    expansion_finished = pyqtSignal()  # Quando a expansão termina
    collapse_finished = pyqtSignal()  # Quando o colapso termina
    
    def __init__(self):
        """Inicializa o widget flutuante"""
        super().__init__()
        
        # Configurações dimensionais (carregadas do config)
        button_config = UI_CONFIG['floating_widget'].get('button', {})
        self.collapsed_size = button_config.get('circular_size', 60)  # Tamanho do círculo
        self.expanded_width = button_config.get('expanded_width', 350)  # Largura da barra expandida
        self.widget_height = button_config.get('expanded_height', 50)   # Altura da barra expandida
        self.opacity_value = UI_CONFIG['floating_widget']['opacity']
        
        # Configurações do botão - Imagens (prioridade)
        self.image_path_collapsed = button_config.get('image_collapsed', None)
        self.image_path_expanded = button_config.get('image_expanded', None)
        self.image_size = button_config.get('image_size', None)  # None = usa button_size
        
        # Configurações do botão - Texto/Emoji (fallback)
        self.icon_collapsed = button_config.get('icon_collapsed', '💬')
        self.icon_expanded = button_config.get('icon_expanded', '➤')
        self.button_size = button_config.get('size', (30, 30))
        self.tooltip_collapsed = button_config.get('tooltip_collapsed', 'Clique para expandir o chat')
        self.tooltip_expanded = button_config.get('tooltip_expanded', 'Digite sua pergunta e pressione Enter')
        
        # Carrega as imagens se especificadas
        self.icon_image_collapsed = None
        self.icon_image_expanded = None
        self.pixmap_collapsed = None
        self.pixmap_expanded = None
        
        if self.image_path_collapsed and self.image_path_collapsed.strip():
            self.pixmap_collapsed = self._load_image(self.image_path_collapsed, self.image_size or self.button_size)
            if self.pixmap_collapsed:
                self.icon_image_collapsed = QIcon(self.pixmap_collapsed)
        
        if self.image_path_expanded and self.image_path_expanded.strip():
            self.pixmap_expanded = self._load_image(self.image_path_expanded, self.image_size or self.button_size)
            if self.pixmap_expanded:
                self.icon_image_expanded = QIcon(self.pixmap_expanded)
        
        # Se expanded não especificado, usa collapsed
        if not self.pixmap_expanded and self.pixmap_collapsed:
            self.pixmap_expanded = self.pixmap_collapsed
            self.icon_image_expanded = self.icon_image_collapsed
        
        # Configurações de cores
        colors_config = UI_CONFIG['floating_widget'].get('colors', {})
        self.color_bg_normal = colors_config.get('background_normal', '#1E3A5F')
        self.color_bg_hover = colors_config.get('background_hover', '#2C5F8D')
        self.color_border = colors_config.get('border_color', '#1E3A5F')
        self.color_icon = colors_config.get('icon_color', '#FFFFFF')
        
        # Estados
        self.is_expanded = False
        self.is_hovered = False
        self.is_animating = False
        
        # Componentes da UI
        self.input_field = None
        self.send_button = None
        self.layout = None
        
        # Animações
        self.expansion_animation = None
        self.pulse_animation = None
        self.animation_timer = QTimer()
        
        self._setup_widget()
        self._setup_ui_components()
        self._setup_animations()
        self._position_widget()
    
    def _setup_widget(self) -> None:
        """Configura as propriedades básicas do widget"""
        # Flags da janela para comportamento flutuante
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # Remove bordas
            Qt.WindowType.WindowStaysOnTopHint |     # Sempre no topo
            Qt.WindowType.Tool |                     # Não aparece na barra de tarefas
            Qt.WindowType.X11BypassWindowManagerHint # Bypass do gerenciador de janelas
        )
        
        # Atributos da janela
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fundo transparente
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # Não rouba foco
        
        # Tamanho inicial (círculo)
        self.setFixedSize(self.collapsed_size, self.collapsed_size)
        
        # Opacidade inicial
        self.setWindowOpacity(self.opacity_value)
        
        # Cursor de mão ao passar o mouse
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Tooltip
        self.setToolTip(self.tooltip_collapsed)
        
        print("[OK] Widget flutuante configurado")
    
    def _setup_ui_components(self) -> None:
        """Configura os componentes da UI (input e botão)"""
        # Layout horizontal para os componentes
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # Campo de input (inicialmente oculto)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite sua pergunta...")
        # REMOVIDO: estilo inline que causa background transparente
        # O estilo será aplicado via _apply_expanded_style() quando expandir
        self.input_field.setVisible(False)
        self.input_field.returnPressed.connect(self._send_message)
        
        # Botão principal (ação dupla: abrir/enviar)
        # Usa ícone se houver imagem, senão usa texto/emoji
        if self.icon_image_collapsed:
            self.action_btn = QPushButton()
            self.action_btn.setIcon(self.icon_image_collapsed)
            self.action_btn.setIconSize(QSize(self.button_size[0], self.button_size[1]))
            # Botão transparente quando usa imagem (o fundo é desenhado pelo paintEvent)
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """)
        else:
            self.action_btn = QPushButton(self.icon_collapsed)
            # Botão com fundo semi-transparente quando usa texto/emoji
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
        
        self.action_btn.setFixedSize(self.button_size[0], self.button_size[1])
        self.action_btn.setVisible(True)  # Sempre visível
        self.action_btn.clicked.connect(self._handle_main_click)
        
        # CORREÇÃO: Adiciona componentes ao layout com stretch factors corretos
        # Input primeiro (esquerda), botão depois (direita)
        self.layout.addWidget(self.input_field, 1)  # Stretch factor = 1 (expande)
        self.layout.addWidget(self.action_btn, 0)   # Stretch factor = 0 (tamanho fixo)
        
        # CORREÇÃO: Força o layout a ser aplicado
        self.layout.setStretchFactor(self.input_field, 1)
        self.layout.setStretchFactor(self.action_btn, 0)
    
    def _setup_animations(self) -> None:
        """Configura as animações do widget"""
        # Timer para animação de pulso (apenas quando colapsado)
        self.animation_timer.timeout.connect(self._animate_pulse)
        self.animation_timer.start(3000)  # Pulsa a cada 3 segundos
        
        # Animação de opacidade para pulso
        self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_animation.setDuration(800)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Animação de expansão/colapso (será configurada dinamicamente)
        self.expansion_animation = QParallelAnimationGroup()
    
    def _position_widget(self) -> None:
        """Posiciona o widget no canto especificado da tela"""
        try:
            from PyQt6.QtWidgets import QApplication
            
            # Obtém a geometria da tela
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # Configurações de posição do config
            position_config = UI_CONFIG['floating_widget'].get('position', {})
            corner = position_config.get('corner', 'bottom-right')
            margin = position_config.get('margin', 20)
            
            # Calcula posição baseada no canto escolhido
            if corner == 'bottom-right':
                x = screen_geometry.width() - self.width() - margin
                y = screen_geometry.height() - self.height() - margin
            elif corner == 'bottom-left':
                x = margin
                y = screen_geometry.height() - self.height() - margin
            elif corner == 'top-right':
                x = screen_geometry.width() - self.width() - margin
                y = margin
            elif corner == 'top-left':
                x = margin
                y = margin
            else:
                # Fallback para bottom-right
                x = screen_geometry.width() - self.width() - margin
                y = screen_geometry.height() - self.height() - margin
            
            self.move(x, y)
            print(f"[OK] Widget posicionado em ({x}, {y}) no canto {corner}")
            
        except Exception as e:
            print(f"[AVISO] Erro ao posicionar widget: {e}")
            # Posição padrão se houver erro
            self.move(100, 100)
    
    def get_input_geometry(self) -> QRect:
        """Retorna a geometria atual do widget para posicionamento do chat"""
        return self.geometry()
    
    def expand_to_input(self) -> None:
        """Expande o widget de círculo para barra de input"""
        print(f"[DEBUG] expand_to_input chamado - Expandido: {self.is_expanded}, Animando: {self.is_animating}")
        
        if self.is_expanded or self.is_animating:
            print("[AVISO] Expansao cancelada - widget ja expandido ou animando")
            return
        
        print("[OK] Iniciando processo de expansao...")
        self.is_animating = True
        
        # Para a animação de pulso
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            print("[INFO] Timer de pulso parado")
        
        # NOVA ABORDAGEM: Redimensiona o widget mantendo posição do botão fixa
        current_rect = self.geometry()
        
        # Calcula nova geometria mantendo a borda direita fixa
        new_width = self.expanded_width
        new_height = self.widget_height
        
        # CORREÇÃO CRÍTICA: Mantém a posição do botão (canto direito) fixa
        # O widget cresce para a esquerda, mas o botão fica na mesma posição absoluta
        button_right_pos = current_rect.right()  # Posição direita atual do botão
        new_x = button_right_pos - new_width     # Nova posição X (cresce para esquerda)
        new_y = current_rect.y() + (self.collapsed_size - new_height) // 2
        
        print(f"[DEBUG] Geometria atual: {current_rect}")
        print(f"[DEBUG] Posicao direita do botao: {button_right_pos}")
        print(f"[DEBUG] Nova geometria: ({new_x}, {new_y}, {new_width}, {new_height})")
        
        # Primeiro, redimensiona o widget sem animação para preparar o layout
        self.setFixedSize(new_width, new_height)
        self.move(new_x, new_y)
        
        # Mostra os componentes imediatamente
        self.input_field.setVisible(True)
        
        # Atualiza ícone/imagem do botão para estado expandido
        if self.icon_image_expanded:
            self.action_btn.setIcon(self.icon_image_expanded)
            self.action_btn.setText("")  # Remove texto se houver
        else:
            self.action_btn.setIcon(QIcon())  # Remove ícone se houver
            self.action_btn.setText(self.icon_expanded)
        
        # Aplica o estilo expandido
        self._apply_expanded_style()
        
        # Força o layout
        self.layout.invalidate()
        self.layout.activate()
        
        # Finaliza a expansão
        self.is_expanded = True
        self.is_animating = False
        self.input_field.setFocus()
        self.setToolTip(self.tooltip_expanded)
        
        # Emite sinal
        self.expansion_finished.emit()
        
        print("[OK] Expansao instantanea concluida")
    
    def collapse_to_circle(self) -> None:
        """Colapsa o widget de barra de input para círculo"""
        if not self.is_expanded or self.is_animating:
            return
        
        self.is_animating = True
        
        # NOVA ABORDAGEM: Colapso instantâneo mantendo posição do botão fixa
        current_rect = self.geometry()
        
        # Calcula posição do círculo mantendo a borda direita fixa
        button_right_pos = current_rect.right()  # Posição direita atual
        new_x = button_right_pos - self.collapsed_size  # Nova posição X
        new_y = current_rect.y() + (self.widget_height - self.collapsed_size) // 2
        
        print(f"[DEBUG] Colapso - Geometria atual: {current_rect}")
        print(f"[DEBUG] Colapso - Nova geometria: ({new_x}, {new_y}, {self.collapsed_size}, {self.collapsed_size})")
        
        # Esconde componentes e volta ao ícone original
        self.input_field.setVisible(False)
        self.input_field.clear()
        # CORREÇÃO: Remove estilo do input quando colapsa
        self.input_field.setStyleSheet("")
        
        # Atualiza ícone/imagem do botão para estado colapsado
        if self.icon_image_collapsed:
            self.action_btn.setIcon(self.icon_image_collapsed)
            self.action_btn.setText("")  # Remove texto se houver
        else:
            self.action_btn.setIcon(QIcon())  # Remove ícone se houver
            self.action_btn.setText(self.icon_collapsed)
        
        # Remove estilo expandido
        self.setStyleSheet("")
        
        # Redimensiona instantaneamente
        self.setFixedSize(self.collapsed_size, self.collapsed_size)
        self.move(new_x, new_y)
        
        # Finaliza o colapso
        self.is_expanded = False
        self.is_animating = False
        self.setToolTip(self.tooltip_collapsed)
        
        # Reinicia animação de pulso
        if not self.animation_timer.isActive():
            self.animation_timer.start(3000)
        
        # Força redesenho
        self.update()
        
        # Emite sinal
        self.collapse_finished.emit()
        
        print("[OK] Colapso instantaneo concluido")
    
    def _on_expansion_finished(self) -> None:
        """Callback executado quando a expansão termina"""
        self.expansion_animation.finished.disconnect()
        self.is_expanded = True
        self.is_animating = False
        
        # Mostra e configura componentes de input
        self.input_field.setVisible(True)
        self.input_field.setFocus()
        
        # Troca o ícone/imagem para envio
        if self.icon_image_expanded:
            self.action_btn.setIcon(self.icon_image_expanded)
            self.action_btn.setText("")  # Remove texto se houver
        else:
            self.action_btn.setIcon(QIcon())  # Remove ícone se houver
            self.action_btn.setText(self.icon_expanded)
        
        # Aplica estilo expandido
        self._apply_expanded_style()
        
        # Atualiza tooltip
        self.setToolTip(self.tooltip_expanded)
        
        # CORREÇÃO: Força o layout a ser recalculado
        self.layout.invalidate()
        self.layout.activate()
        
        # Força redesenho
        self.update()
        
        # Emite sinal
        self.expansion_finished.emit()
        
        print("[OK] Expansao concluida")
    
    def _on_collapse_finished(self) -> None:
        """Callback executado quando o colapso termina"""
        self.expansion_animation.finished.disconnect()
        self.is_expanded = False
        self.is_animating = False
        
        # CORREÇÃO: Remove estilo quando colapsado (volta ao desenho customizado)
        self.setStyleSheet("")
        
        # Atualiza tooltip
        self.setToolTip(self.tooltip_collapsed)
        
        # Reinicia animação de pulso
        if not self.animation_timer.isActive():
            self.animation_timer.start(3000)
        
        # Força redesenho
        self.update()
        
        # Emite sinal
        self.collapse_finished.emit()
        
        print("[OK] Colapso concluido")
    
    def _handle_main_click(self) -> None:
        """Manipula clique no botão principal (ação dupla: abrir/enviar)"""
        if self.is_expanded:
            # Se expandido, funciona como botão de envio
            self._send_message()
        else:
            # Se colapsado, funciona como botão de abrir
            if not self.is_animating:
                self.expand_to_input()
    
    def _send_message(self) -> None:
        """Envia a mensagem digitada"""
        message = self.input_field.text().strip()
        if message:
            self.message_sent.emit(message)
            self.input_field.clear()
    
    def paintEvent(self, event) -> None:
        """
        Desenha o widget personalizado baseado no estado atual
        
        Args:
            event: Evento de pintura
        """
        # CORREÇÃO: Só desenha fundo customizado quando colapsado
        if not self.is_expanded:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Desenha o fundo circular apenas quando colapsado
            self._draw_background(painter)
            
            # Desenha o ícone no centro
            self._draw_icon(painter)
            
            painter.end()
        # CORREÇÃO: Quando expandido, não desenha nada customizado
        # O stylesheet cuida do visual
    
    def _draw_background(self, painter: QPainter) -> None:
        """Desenha o fundo do widget"""
        # Cores do config (converte hex para QColor)
        if self.is_hovered:
            bg_color = QColor(self.color_bg_hover)
            bg_color.setAlpha(240)  # Adiciona transparência
        else:
            bg_color = QColor(self.color_bg_normal)
            bg_color.setAlpha(220)  # Adiciona transparência
        
        border_color = QColor(self.color_border)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        
        margin = 2
        if self.is_expanded:
            painter.drawRoundedRect(
                margin, margin,
                self.width() - 2 * margin,
                self.height() - 2 * margin,
                self.height() // 2,
                self.height() // 2
            )
        else:
            painter.drawEllipse(
                margin, margin,
                self.width() - 2 * margin,
                self.height() - 2 * margin
            )
    
    def _draw_icon(self, painter: QPainter) -> None:
        """Desenha o ícone no centro do widget (apenas quando não há imagem configurada)"""
        # Se houver imagem configurada, não desenha aqui (o botão QPushButton já exibe)
        # Só desenha quando usa texto/emoji
        if not self.pixmap_collapsed or not self.icon_image_collapsed:
            font = QFont("Segoe UI Symbol", 20, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(self.color_icon))
            
            # Usa o ícone configurado
            icon_text = self.icon_collapsed if not self.is_expanded else self.icon_expanded
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, icon_text)
    
    def mousePressEvent(self, event) -> None:
        """
        Manipula cliques no widget (apenas quando colapsado)
        
        Args:
            event: Evento do mouse
        """
        if event.button() == Qt.MouseButton.LeftButton and not self.is_expanded:
            print(f"🖱️ Clique detectado - Expandido: {self.is_expanded}, Animando: {self.is_animating}")
            if not self.is_animating:
                print("[OK] Iniciando expansao...")
                self.expand_to_input()
            self._animate_click()
    
    def enterEvent(self, event) -> None:
        """
        Manipula entrada do mouse no widget
        
        Args:
            event: Evento de entrada
        """
        self.is_hovered = True
        self.setWindowOpacity(1.0)  # Opacidade total no hover
        self.update()  # Redesenha
    
    def leaveEvent(self, event) -> None:
        """
        Manipula saída do mouse do widget
        
        Args:
            event: Evento de saída
        """
        self.is_hovered = False
        self.setWindowOpacity(self.opacity_value)  # Volta à opacidade normal
        self.update()  # Redesenha
    
    def _animate_pulse(self) -> None:
        """Anima um pulso sutil para chamar atenção (apenas quando colapsado)"""
        if not self.is_hovered and not self.is_expanded:  # Só anima se colapsado e sem hover
            # Animação de opacidade
            self.pulse_animation.setStartValue(self.opacity_value)
            self.pulse_animation.setEndValue(self.opacity_value + 0.2)
            self.pulse_animation.finished.connect(self._pulse_back)
            self.pulse_animation.start()
    
    def _pulse_back(self) -> None:
        """Volta a opacidade ao normal após o pulso"""
        self.pulse_animation.finished.disconnect()
        self.pulse_animation.setStartValue(self.windowOpacity())
        self.pulse_animation.setEndValue(self.opacity_value)
        self.pulse_animation.start()
    
    def _animate_click(self) -> None:
        """Anima um feedback visual ao clicar"""
        # Animação rápida de opacidade
        click_animation = QPropertyAnimation(self, b"windowOpacity")
        click_animation.setDuration(150)
        click_animation.setStartValue(1.0)
        click_animation.setEndValue(0.7)
        click_animation.finished.connect(
            lambda: self.setWindowOpacity(0.95 if self.is_expanded else self.opacity_value)
        )
        click_animation.start()
    
    def show_notification(self, message: str) -> None:
        """
        Mostra uma notificação temporária no widget
        
        Args:
            message: Mensagem a ser exibida
        """
        # Atualiza tooltip temporariamente
        original_tooltip = self.toolTip()
        self.setToolTip(f"💬 {message}")
        
        # Volta ao tooltip original após 3 segundos
        QTimer.singleShot(3000, lambda: self.setToolTip(original_tooltip))
        
        # Anima para chamar atenção se estiver colapsado
        if not self.is_expanded:
            self._animate_pulse()
    
    def set_position(self, x: int, y: int) -> None:
        """
        Define uma nova posição para o widget
        
        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        self.move(x, y)
    
    def toggle_visibility(self) -> None:
        """Alterna a visibilidade do widget"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
    
    def close_input(self) -> None:
        """Fecha a barra de input e volta ao estado de círculo"""
        if self.is_expanded:
            self.collapse_to_circle()
    
    def _apply_expanded_style(self) -> None:
        """Aplica o estilo quando expandido"""
        # Cores do config ou valores padrão
        colors_config = UI_CONFIG['floating_widget'].get('colors', {})
        bg_expanded = colors_config.get('background_expanded', '#FFFFFF')
        border_expanded = colors_config.get('border_expanded', '#DEE2E6')
        
        # Cores do tema geral (fallback para cores padrão)
        theme_colors = UI_CONFIG.get('colors', {})
        input_bg = theme_colors.get('background', '#F8F9FA')
        input_text = theme_colors.get('text_primary', '#1E3A5F')
        input_placeholder = theme_colors.get('text_muted', '#ADB5BD')
        button_bg = theme_colors.get('secondary', '#2C5F8D')
        button_bg_hover = theme_colors.get('primary', '#1E3A5F')
        
        # Estilo corporativo usando cores configuráveis
        self.setStyleSheet(f"""
            FloatingWidget {{
                background-color: {bg_expanded};
                border: 1px solid {border_expanded};
                border-radius: 25px;
                box-shadow: 0 4px 12px rgba(30, 58, 95, 0.12);
            }}
            QLineEdit {{
                border: 1px solid {border_expanded};
                background-color: {input_bg};
                color: {input_text};
                font-size: 13px;
                padding: 8px 12px;
                min-width: 200px;
                border-radius: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {button_bg};
                background-color: {bg_expanded};
            }}
            QLineEdit::placeholder {{
                color: {input_placeholder};
            }}
            QPushButton {{
                background-color: {button_bg};
                border: none;
                border-radius: 15px;
                color: white;
                font-weight: 500;
                font-size: 14px;
                min-width: {self.button_size[0]}px;
                max-width: {self.button_size[0]}px;
                min-height: {self.button_size[1]}px;
                max-height: {self.button_size[1]}px;
            }}
            QPushButton:hover {{
                background-color: {button_bg_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_bg_hover};
                opacity: 0.8;
            }}
        """)
        
        # Aplica estilo diretamente ao input
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {border_expanded} !important;
                background-color: {input_bg} !important;
                color: {input_text} !important;
                font-size: 13px;
                padding: 8px 12px;
                border-radius: 20px;
            }}
            QLineEdit::placeholder {{
                color: {input_placeholder};
            }}
            QLineEdit:focus {{
                border: 2px solid {button_bg} !important;
                background-color: {bg_expanded} !important;
            }}
        """)
        
        self.input_field.update()
        self.update()
    
    def _load_image(self, image_path: str, size: tuple) -> QPixmap:
        """
        Carrega uma imagem do disco e redimensiona se necessário
        
        Args:
            image_path: Caminho para a imagem (relativo ao BASE_DIR ou absoluto)
            size: Tupla (largura, altura) para redimensionar
            
        Returns:
            QPixmap da imagem ou None se não conseguir carregar
        """
        try:
            # Tenta caminho absoluto primeiro
            full_path = Path(image_path)
            if not full_path.is_absolute():
                # Se relativo, assume a partir do BASE_DIR
                full_path = BASE_DIR / image_path
            
            if not full_path.exists():
                print(f"[AVISO] Imagem nao encontrada: {full_path}")
                return None
            
            # Carrega a imagem
            pixmap = QPixmap(str(full_path))
            
            if pixmap.isNull():
                print(f"[AVISO] Erro ao carregar imagem: {full_path}")
                return None
            
            # Redimensiona se necessário
            if size and (size[0] > 0 and size[1] > 0):
                pixmap = pixmap.scaled(
                    size[0],
                    size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            print(f"[OK] Imagem carregada: {full_path} ({pixmap.width()}x{pixmap.height()})")
            return pixmap
            
        except Exception as e:
            print(f"[ERRO] Erro ao processar imagem {image_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup(self) -> None:
        """Limpa recursos do widget"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        if self.pulse_animation and self.pulse_animation.state() == QPropertyAnimation.State.Running:
            self.pulse_animation.stop()
        
        if self.expansion_animation and self.expansion_animation.state() == QPropertyAnimation.State.Running:
            self.expansion_animation.stop()
        
        print("[OK] Recursos do widget flutuante limpos")