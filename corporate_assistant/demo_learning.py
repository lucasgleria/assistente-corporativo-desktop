"""
Demonstração do sistema de aprendizado em tempo real
Mostra como o sistema aprende com feedback negativo instantaneamente
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.models import Base
from app.database.repository import FAQRepository, DynamicPenaltyRepository
from app.core.nlp_engine import SearchEngine


def demonstrate_learning():
    """Demonstra o aprendizado em tempo real"""
    print("🧠 DEMONSTRAÇÃO DE APRENDIZADO EM TEMPO REAL")
    print("=" * 60)
    
    # Inicializa componentes
    search_engine = SearchEngine()
    penalty_repo = DynamicPenaltyRepository()
    
    if not search_engine.is_available():
        print("❌ Modelo NLP não disponível para demonstração")
        return False
    
    # Pergunta de teste
    test_question = "Como pedir férias na empresa?"
    
    print(f"📝 Pergunta de teste: '{test_question}'")
    print()
    
    # 1. Busca inicial (sem aprendizado)
    print("1️⃣ BUSCA INICIAL (sem penalidades)")
    print("-" * 40)
    
    initial_results = search_engine.search(test_question, top_k=3, apply_learning=False)
    
    if not initial_results:
        print("❌ Nenhum resultado encontrado")
        return False
    
    print("Resultados encontrados:")
    for i, result in enumerate(initial_results, 1):
        print(f"  {i}. FAQ #{result.faq.id}: {result.confidence:.1%} confiança")
        print(f"     '{result.faq.question[:60]}...'")
    
    # Seleciona a melhor resposta para "penalizar"
    best_result = initial_results[0]
    faq_to_penalize = best_result.faq.id
    
    print(f"\n🎯 Vamos simular feedback NEGATIVO para FAQ #{faq_to_penalize}")
    print()
    
    # 2. Aplica feedback negativo (aprendizado)
    print("2️⃣ APLICANDO APRENDIZADO (feedback negativo)")
    print("-" * 40)
    
    learning_success = search_engine.apply_negative_feedback(
        user_question=test_question,
        faq_id=faq_to_penalize,
        penalty_factor=0.2  # Reduz score em 80%
    )
    
    if learning_success:
        print("✅ Aprendizado aplicado com sucesso!")
    else:
        print("❌ Falha ao aplicar aprendizado")
        return False
    
    print()
    
    # 3. Busca após aprendizado
    print("3️⃣ BUSCA APÓS APRENDIZADO (com penalidades)")
    print("-" * 40)
    
    learned_results = search_engine.search(test_question, top_k=3, apply_learning=True)
    
    print("Resultados após aprendizado:")
    for i, result in enumerate(learned_results, 1):
        print(f"  {i}. FAQ #{result.faq.id}: {result.confidence:.1%} confiança")
        print(f"     '{result.faq.question[:60]}...'")
        
        # Indica se houve mudança
        if result.faq.id == faq_to_penalize:
            print(f"     🚫 PENALIZADA (era {initial_results[0].confidence:.1%})")
    
    print()
    
    # 4. Comparação dos resultados
    print("4️⃣ ANÁLISE DO APRENDIZADO")
    print("-" * 40)
    
    initial_best = initial_results[0]
    learned_best = learned_results[0]
    
    if initial_best.faq.id != learned_best.faq.id:
        print("🎉 APRENDIZADO FUNCIONOU!")
        print(f"   Antes: FAQ #{initial_best.faq.id} era a melhor ({initial_best.confidence:.1%})")
        print(f"   Depois: FAQ #{learned_best.faq.id} agora é a melhor ({learned_best.confidence:.1%})")
        print("   O sistema aprendeu a não sugerir a resposta com feedback negativo!")
    else:
        print("ℹ️ A mesma FAQ ainda é a melhor, mas com score reduzido")
        print(f"   Antes: {initial_best.confidence:.1%}")
        print(f"   Depois: {learned_best.confidence:.1%}")
    
    return True


def test_similar_questions():
    """Testa se o aprendizado se aplica a perguntas similares"""
    print("\n🔄 TESTE COM PERGUNTAS SIMILARES")
    print("=" * 60)
    
    search_engine = SearchEngine()
    
    if not search_engine.is_available():
        return False
    
    # Perguntas similares para testar
    similar_questions = [
        "Como solicitar férias?",
        "Quero tirar férias, como faço?",
        "Processo para pedir férias",
        "Como funciona a solicitação de férias?"
    ]
    
    print("Testando se o aprendizado se aplica a perguntas similares:")
    print()
    
    for i, question in enumerate(similar_questions, 1):
        print(f"{i}. '{question}'")
        
        results = search_engine.search(question, top_k=1, apply_learning=True)
        
        if results:
            result = results[0]
            print(f"   → FAQ #{result.faq.id}: {result.confidence:.1%} confiança")
            
            # Verifica se há penalidade aplicada
            penalty_factor = search_engine.penalty_repository.calculate_penalty_for_question(
                result.faq.id, 
                search_engine.generate_embedding(question)
            )
            
            if penalty_factor < 1.0:
                print(f"   🚫 Penalidade ativa: {(1-penalty_factor)*100:.0f}% redução")
            else:
                print("   ✅ Sem penalidade")
        else:
            print("   ❌ Nenhum resultado")
        
        print()
    
    return True


def show_penalty_stats():
    """Mostra estatísticas das penalidades"""
    print("📊 ESTATÍSTICAS DE APRENDIZADO")
    print("=" * 60)
    
    try:
        penalty_repo = DynamicPenaltyRepository()
        stats = penalty_repo.get_penalty_stats()
        
        print(f"Total de penalidades: {stats['total_penalties']}")
        print(f"Penalidades ativas: {stats['active_penalties']}")
        print(f"Penalidades expiradas: {stats['expired_penalties']}")
        
        if stats['most_penalized_faqs']:
            print("\nFAQs mais penalizadas:")
            for item in stats['most_penalized_faqs']:
                print(f"  • FAQ #{item['faq_id']}: {item['penalty_count']} penalidades")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return False


def main():
    """Função principal da demonstração"""
    print("=" * 70)
    print("  DEMONSTRAÇÃO DE APRENDIZADO EM TEMPO REAL")
    print("  Sistema aprende instantaneamente com feedback negativo")
    print("=" * 70)
    print()
    
    try:
        # Inicializa banco
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        Base.metadata.create_all(engine)
        
        # Verifica se há FAQs
        faq_repo = FAQRepository()
        if faq_repo.count() == 0:
            print("❌ Nenhuma FAQ encontrada!")
            print("💡 Execute primeiro: python add_sample_data.py")
            return 1
        
        print(f"✅ Sistema pronto com {faq_repo.count()} FAQs")
        print()
        
        # Executa demonstrações
        success = True
        
        # 1. Demonstração principal
        if not demonstrate_learning():
            success = False
        
        # 2. Teste com perguntas similares
        if success and not test_similar_questions():
            success = False
        
        # 3. Estatísticas
        if success:
            show_penalty_stats()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✨ O sistema agora aprende em tempo real com feedback negativo")
            print("🔍 Use 'python view_feedback_stats.py' para análise detalhada")
        else:
            print("❌ Alguns testes falharam")
        print("=" * 70)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())