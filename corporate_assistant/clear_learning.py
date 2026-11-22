"""
Script para limpar o aprendizado e resetar o sistema
Útil para testes e demonstrações
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.nlp_engine import SearchEngine


def main():
    """Limpa todas as penalidades do sistema"""
    print("🧹 LIMPANDO SISTEMA DE APRENDIZADO")
    print("=" * 40)
    
    try:
        # Obtém instância do SearchEngine
        engine = SearchEngine()
        
        # Mostra estatísticas antes
        stats_before = engine.get_penalty_stats()
        print(f"Penalidades antes: {stats_before.get('total_penalties', 0)}")
        
        # Limpa penalidades
        engine.clear_penalties()
        
        # Mostra estatísticas depois
        stats_after = engine.get_penalty_stats()
        print(f"Penalidades depois: {stats_after.get('total_penalties', 0)}")
        
        print("✅ Sistema de aprendizado resetado!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())