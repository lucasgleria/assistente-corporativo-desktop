"""
Script para desabilitar sistema de feedback para produção
Execute este script antes de distribuir o sistema final
"""

import sys
import os
from pathlib import Path


def disable_feedback_in_config():
    """Desabilita o sistema de feedback no arquivo de configuração"""
    config_file = Path("app/config.py")
    
    if not config_file.exists():
        print("❌ Arquivo de configuração não encontrado!")
        return False
    
    try:
        # Lê o arquivo atual
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui as configurações de desenvolvimento
        new_content = content.replace(
            'DEVELOPMENT_CONFIG = {\n'
            '    "feedback_enabled": True,  # Habilita sistema de feedback (DESABILITAR EM PRODUÇÃO)\n'
            '    "show_debug_info": True,   # Mostra informações de debug\n'
            '    "log_feedback": True,      # Registra feedback no console\n'
            '    "export_training_data": True  # Permite exportar dados de treinamento\n'
            '}',
            'DEVELOPMENT_CONFIG = {\n'
            '    "feedback_enabled": False,  # Sistema de feedback DESABILITADO para produção\n'
            '    "show_debug_info": False,   # Debug desabilitado\n'
            '    "log_feedback": False,      # Log de feedback desabilitado\n'
            '    "export_training_data": False  # Export de dados desabilitado\n'
            '}'
        )
        
        # Salva o arquivo modificado
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Sistema de feedback desabilitado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao modificar configuração: {e}")
        return False


def remove_feedback_files():
    """Remove arquivos relacionados ao sistema de feedback"""
    feedback_files = [
        "view_feedback_stats.py",
        "disable_feedback.py"  # Remove este próprio script
    ]
    
    removed_count = 0
    
    for file_name in feedback_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️ Removido: {file_name}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Erro ao remover {file_name}: {e}")
    
    return removed_count


def clean_feedback_data():
    """Remove dados de feedback do banco (opcional)"""
    response = input("\n⚠️ Deseja remover todos os dados de feedback do banco? (s/N): ")
    
    if response.lower() not in ['s', 'sim', 'y', 'yes']:
        print("📊 Dados de feedback mantidos no banco.")
        return False
    
    try:
        # Adiciona o diretório app ao path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.database.connection import DatabaseManager
        from app.database.models import UserFeedback
        
        # Conecta ao banco
        db_manager = DatabaseManager()
        
        with db_manager.get_session() as session:
            # Conta feedbacks existentes
            feedback_count = session.query(UserFeedback).count()
            
            if feedback_count == 0:
                print("📊 Nenhum dado de feedback encontrado.")
                return True
            
            print(f"📊 Encontrados {feedback_count} registros de feedback.")
            
            # Confirma remoção
            confirm = input(f"Confirma remoção de {feedback_count} registros? (s/N): ")
            if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada.")
                return False
            
            # Remove todos os feedbacks
            session.query(UserFeedback).delete()
            session.commit()
            
            print(f"✅ {feedback_count} registros de feedback removidos.")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao limpar dados de feedback: {e}")
        return False


def update_welcome_message():
    """Remove referência ao feedback da mensagem de boas-vindas"""
    try:
        # Adiciona o diretório app ao path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        chat_window_file = Path("app/ui/chat_window.py")
        
        if not chat_window_file.exists():
            print("⚠️ Arquivo chat_window.py não encontrado.")
            return False
        
        # Lê o arquivo
        with open(chat_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove a linha sobre feedback da mensagem de boas-vindas
        new_content = content.replace(
            '        # Adiciona informação sobre feedback se habilitado\n'
            '        if UI_CONFIG[\'feedback\'][\'enabled\']:\n'
            '            welcome_msg += "\\n\\n💡 Dica: Use os botões 👍👎 para avaliar as respostas e ajudar a melhorar o sistema!"',
            '        # Sistema de feedback desabilitado em produção'
        )
        
        # Salva o arquivo
        with open(chat_window_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Mensagem de boas-vindas atualizada.")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar mensagem: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("  PREPARAÇÃO PARA PRODUÇÃO")
    print("  Desabilitando Sistema de Feedback")
    print("=" * 60)
    print()
    
    print("Este script irá:")
    print("1. ✏️ Desabilitar feedback no arquivo de configuração")
    print("2. 🗑️ Remover scripts de desenvolvimento")
    print("3. 🧹 Limpar dados de feedback (opcional)")
    print("4. 📝 Atualizar mensagens da interface")
    print()
    
    response = input("Continuar? (s/N): ")
    if response.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada.")
        return 1
    
    print("\n" + "=" * 40)
    
    success_count = 0
    total_steps = 4
    
    # 1. Desabilita feedback na configuração
    print("1️⃣ Desabilitando feedback na configuração...")
    if disable_feedback_in_config():
        success_count += 1
    
    # 2. Remove arquivos de desenvolvimento
    print("\n2️⃣ Removendo arquivos de desenvolvimento...")
    removed_files = remove_feedback_files()
    if removed_files > 0:
        success_count += 1
    
    # 3. Limpa dados de feedback (opcional)
    print("\n3️⃣ Limpando dados de feedback...")
    if clean_feedback_data():
        success_count += 1
    
    # 4. Atualiza mensagens
    print("\n4️⃣ Atualizando interface...")
    if update_welcome_message():
        success_count += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print(f"✅ CONCLUÍDO: {success_count}/{total_steps} etapas realizadas com sucesso")
    
    if success_count == total_steps:
        print("🎉 Sistema preparado para produção!")
        print("📦 O sistema de feedback foi completamente removido.")
        print("🚀 Agora você pode distribuir o assistente corporativo.")
    else:
        print("⚠️ Algumas etapas falharam. Verifique os erros acima.")
    
    print("=" * 60)
    
    return 0 if success_count == total_steps else 1


if __name__ == "__main__":
    sys.exit(main())