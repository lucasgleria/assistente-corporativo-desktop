"""
Estilos CSS centralizados para a interface do chatbot
Design profissional com alto contraste e acessibilidade
"""

from app.config import UI_CONFIG

# Extrai configurações de cores e tipografia
colors = UI_CONFIG["colors"]
typography = UI_CONFIG["typography"]
spacing = UI_CONFIG["spacing"]
border_radius = UI_CONFIG["border_radius"]


class ChatStyles:
    """Estilos para os componentes do chat"""
    
    @staticmethod
    def get_floating_widget_collapsed():
        """Estilo para o widget flutuante colapsado (círculo)"""
        return f"""
            FloatingWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                border: 2px solid {colors['white']};
                border-radius: {border_radius['circle']};
                box-shadow: 0 4px 12px {colors['shadow']};
            }}
        """
    
    @staticmethod
    def get_floating_widget_expanded():
        """Estilo para o widget flutuante expandido (barra de input)"""
        return f"""
            FloatingWidget {{
                background: {colors['surface']};
                border: 2px solid {colors['primary']};
                border-radius: {border_radius['large']};
                box-shadow: 0 6px 20px {colors['shadow']};
            }}
            
            QLineEdit {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['medium']};
                color: {colors['text_primary']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_normal']};
                font-weight: {typography['font_weight_normal']};
                padding: {spacing['sm']} {spacing['md']};
                min-width: 200px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {colors['secondary']};
                background-color: {colors['white']};
            }}
            
            QLineEdit::placeholder {{
                color: {colors['text_secondary']};
                font-style: italic;
            }}
            
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['secondary']}, 
                    stop:1 {colors['primary']});
                border: none;
                border-radius: {border_radius['medium']};
                color: {colors['white']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_medium']};
                font-weight: {typography['font_weight_medium']};
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['secondary']}, 
                    stop:1 {colors['secondary']});
                transform: scale(1.05);
            }}
            
            QPushButton:pressed {{
                background: {colors['primary']};
                transform: scale(0.95);
            }}
        """
    
    @staticmethod
    def get_chat_window():
        """Estilo para a janela principal do chat"""
        return f"""
            QWidget {{
                background-color: {colors['background']};
                font-family: {typography['font_family']};
            }}
            
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['large']};
                box-shadow: 0 2px 8px {colors['shadow']};
            }}
        """
    
    @staticmethod
    def get_chat_header():
        """Estilo para o cabeçalho da janela de chat"""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                border: none;
                border-radius: {border_radius['large']} {border_radius['large']} 0px 0px;
                padding: {spacing['md']} {spacing['lg']};
                box-shadow: 0 2px 4px {colors['shadow']};
            }}
            
            QLabel {{
                color: {colors['white']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_medium']};
                font-weight: {typography['font_weight_bold']};
                background: transparent;
                border: none;
                letter-spacing: 0.5px;
            }}
            
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {border_radius['small']};
                color: {colors['white']};
                font-weight: {typography['font_weight_medium']};
                font-size: {typography['font_size_medium']};
                padding: {spacing['xs']} {spacing['sm']};
                min-width: 28px;
                min-height: 28px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
            }}
            
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """
    
    @staticmethod
    def get_user_message():
        """Estilo para mensagens do usuário"""
        return f"""
            QFrame {{
                background-color: {colors['user_message']};
                border: none;
                border-radius: {border_radius['medium']} {border_radius['medium']} {border_radius['small']} {border_radius['medium']};
                margin: {spacing['xs']} {spacing['md']} {spacing['xs']} {spacing['sm']};
                padding: {spacing['sm']} {spacing['md']};
                box-shadow: 0 2px 4px {colors['shadow']};
            }}
            
            QLabel {{
                color: {colors['white']};
                background: transparent;
                border: none;
                font-family: {typography['font_family']};
                font-size: {typography['font_size_normal']};
                font-weight: {typography['font_weight_normal']};
                line-height: 1.6;
            }}
        """
    
    @staticmethod
    def get_bot_message():
        """Estilo para mensagens do bot"""
        return f"""
            QFrame {{
                background-color: {colors['bot_message']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['medium']} {border_radius['medium']} {border_radius['medium']} {border_radius['small']};
                margin: {spacing['xs']} {spacing['sm']} {spacing['xs']} {spacing['md']};
                padding: {spacing['sm']} {spacing['md']};
                box-shadow: 0 2px 4px {colors['shadow']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
                background: transparent;
                border: none;
                font-family: {typography['font_family']};
                font-size: {typography['font_size_normal']};
                font-weight: {typography['font_weight_normal']};
                line-height: 1.6;
            }}
        """
    
    @staticmethod
    def get_feedback_buttons():
        """Estilo para botões de feedback"""
        return f"""
            QToolButton {{
                background-color: {colors['light']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['small']};
                color: {colors['text_secondary']};
                font-size: {typography['font_size_small']};
                padding: {spacing['xs']} {spacing['sm']};
                min-width: 32px;
                min-height: 32px;
            }}
            
            QToolButton:hover {{
                background-color: {colors['surface']};
                border-color: {colors['secondary']};
                color: {colors['secondary']};
            }}
            
            QToolButton:pressed {{
                background-color: {colors['border']};
            }}
        """
    
    @staticmethod
    def get_feedback_positive():
        """Estilo para feedback positivo ativo"""
        return f"""
            QToolButton {{
                background-color: {colors['success']};
                border: 1px solid {colors['success']};
                color: {colors['white']};
            }}
        """
    
    @staticmethod
    def get_feedback_negative():
        """Estilo para feedback negativo ativo"""
        return f"""
            QToolButton {{
                background-color: {colors['danger']};
                border: 1px solid {colors['danger']};
                color: {colors['white']};
            }}
        """
    
    @staticmethod
    def get_progress_bar():
        """Estilo para barra de progresso"""
        return f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: {border_radius['small']};
                text-align: center;
                background-color: {colors['light']};
                color: {colors['text_primary']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_small']};
                font-weight: {typography['font_weight_medium']};
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['secondary']}, 
                    stop:1 {colors['primary']});
                border-radius: {border_radius['small']};
            }}
        """
    
    @staticmethod
    def get_learning_controls():
        """Estilo para controles de aprendizado"""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['light']}, 
                    stop:1 {colors['background']});
                border: 1px solid {colors['border']};
                border-radius: {border_radius['medium']};
                margin: {spacing['xs']};
                padding: {spacing['sm']};
            }}
            
            QLabel {{
                color: {colors['primary']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_medium']};
                font-weight: {typography['font_weight_bold']};
                background: transparent;
                border: none;
            }}
            
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['small']};
                color: {colors['text_primary']};
                font-size: {typography['font_size_medium']};
                padding: {spacing['xs']};
            }}
            
            QPushButton:hover {{
                background-color: {colors['secondary']};
                border-color: {colors['secondary']};
                color: {colors['white']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
        """
    
    @staticmethod
    def get_status_label():
        """Estilo para label de status"""
        return f"""
            QLabel {{
                color: {colors['text_secondary']};
                background: transparent;
                border: none;
                font-family: {typography['font_family']};
                font-size: {typography['font_size_small']};
                font-weight: {typography['font_weight_normal']};
                padding: {spacing['xs']};
            }}
        """
    
    @staticmethod
    def get_scroll_area():
        """Estilo para área de scroll"""
        return f"""
            QScrollArea {{
                border: none;
                background-color: {colors['background']};
            }}
            
            QScrollBar:vertical {{
                background-color: {colors['light']};
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['secondary']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
    
    @staticmethod
    def get_confidence_label(confidence: float):
        """Estilo para label de confiança baseado no valor"""
        if confidence >= 0.8:
            color = colors['success']
        elif confidence >= 0.6:
            color = colors['warning']
        else:
            color = colors['danger']
        
        return f"""
            QLabel {{
                color: {color};
                background: transparent;
                border: none;
                font-family: {typography['font_family']};
                font-size: {typography['font_size_small']};
                font-weight: {typography['font_weight_medium']};
            }}
        """


class SystemTrayStyles:
    """Estilos para o sistema de bandeja"""
    
    @staticmethod
    def get_menu():
        """Estilo para menu da bandeja do sistema"""
        return f"""
            QMenu {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius['medium']};
                padding: {spacing['xs']};
            }}
            
            QMenu::item {{
                background-color: transparent;
                color: {colors['text_primary']};
                font-family: {typography['font_family']};
                font-size: {typography['font_size_normal']};
                padding: {spacing['sm']} {spacing['md']};
                border-radius: {border_radius['small']};
            }}
            
            QMenu::item:selected {{
                background-color: {colors['secondary']};
                color: {colors['white']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {colors['border']};
                margin: {spacing['xs']} 0px;
            }}
        """


def apply_dark_theme():
    """Aplica tema escuro (para futuras implementações)"""
    # Implementação futura para tema escuro
    pass


def apply_high_contrast_theme():
    """Aplica tema de alto contraste para acessibilidade"""
    # Implementação futura para alto contraste
    pass