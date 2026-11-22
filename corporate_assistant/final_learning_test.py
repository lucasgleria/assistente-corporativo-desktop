"""
Teste final do sistema de aprendizado
Simula exatamente o cenário do usuário: mesma pergunta, feedback negativo repetido
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.nlp_engine import SearchEngine
from app.database.repository import FeedbackRepository


def simulate_user_scenario():
    """Simula o cenário exato do usuário"""
    print("🎭 SIMULAÇÃO DO CENÁRIO DO USUÁRIO")
    print("=" * 50)
    
    # Limpa aprendizado anterior
    engine = SearchEngine()
    engine.clear_penalties()
    
    feedback_repo = FeedbackRepository()
    
    # Pergunta do usuário (com erro de digitação como no log)
    user_question = "Como solicitar"  # Pergunta similar ao log
    
    print(f"👤 Usuário pergunta: '{user_question}'")
    print()
    
    # Simula múltiplas tentativas como no log
    for attempt in range(1, 5):
        print(f"🔄 TENTATIVA {attempt}")
        print("-" * 30)
        
        # Busca
        results = engine.search(user_question, top_k=3)
        
        if not results:
            print("❌ Nenhum resultado")
            continue
        
        best_result = results[0]
        print(f"🤖 Sistema responde: FAQ #{best_result.faq.id} ({best_result.confidence:.1%})")
        print(f"   '{best_result.faq.question[:50]}...'")
        
        # Simula feedback negativo do usuário
        print("👤 Usuário clica 👎 (feedback negativo)")
        
        # Salva feedback no banco
        try:
            user_embedding = engine.generate_embedding(user_question)
            feedback = feedback_repo.create_feedback(
                user_question=user_question,
                faq_id=best_result.faq.id,
                is_positive=False,
                confidence_score=best_result.confidence,
                user_question_embedding=user_embedding
            )
            print(f"✓ Feedback salvo no banco: ID #{feedback.id}")
        except Exception as e:
            print(f"⚠ Erro ao salvar feedback: {e}")
        
        # Aplica aprendizado
        learning_success = engine.apply_negative_feedback(
            user_question=user_question,
            faq_id=best_result.faq.id,
            penalty_factor=0.4  # 60% redução (menos agressivo)
        )
        
        if learning_success:
            print("🎯 Aprendizado aplicado!")
        else:
            print("❌ Falha no aprendizado")
        
        # Mostra estatísticas
        stats = engine.get_penalty_stats()
        print(f"📊 Penalidades ativas: {stats.get('total_penalties', 0)}")
        
        print()
    
    # Teste final - verifica se o sistema aprendeu
    print("🧪 TESTE FINAL - O SISTEMA APRENDEU?")
    print("-" * 40)
    
    final_results = engine.search(user_question, top_k=3)
    
    if final_results:
        final_best = final_results[0]
        print(f"🎯 Melhor resposta agora: FAQ #{final_best.faq.id} ({final_best.confidence:.1%})")
        print(f"   '{final_best.faq.question[:50]}...'")
        
        # Verifica se mudou
        first_attempt_faq = 1  # Assumindo que era FAQ #1 inicialmente
        if final_best.faq.id != first_attempt_faq:
            print("🎉 SUCESSO! O sistema aprendeu e mudou a resposta!")
            return True
        else:
            # Verifica se pelo menos foi penalizada
            penalized = next((r for r in final_results if r.faq.id == first_attempt_faq), None)
            if penalized and penalized.confidence < 0.5:  # Significativamente reduzida
                print("✅ SUCESSO! A resposta foi penalizada significativamente!")
                return True
            else:
                print("❌ FALHA! O sistema não aprendeu efetivamente")
                return False
    else:
        print("❌ Nenhum resultado no teste final")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("  TESTE FINAL - RESOLUÇÃO DO PROBLEMA DO USUÁRIO")
    print("  Simula: pergunta repetida + feedback negativo repetido")
    print("=" * 60)
    print()
    
    try:
        from app.database.repository import FAQRepository
        
        # Verifica se há FAQs
        faq_repo = FAQRepository()
        if faq_repo.count() == 0:
            print("❌ Nenhuma FAQ encontrada!")
            print("💡 Execute primeiro: python add_sample_data.py")
            return 1
        
        print(f"✅ Sistema pronto com {faq_repo.count()} FAQs")
        print()
        
        success = simulate_user_scenario()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 PROBLEMA RESOLVIDO!")
            print("✨ O sistema agora aprende corretamente com feedback negativo")
            print("🚀 Não vai mais insistir em respostas ruins")
        else:
            print("❌ Problema ainda existe")
            print("🔧 Necessário investigar mais")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())