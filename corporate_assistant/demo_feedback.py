"""
Demonstração do sistema de feedback
Simula interações do usuário para mostrar como o feedback funciona
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.models import Base
from app.database.repository import FAQRepository, FeedbackRepository
from app.core.nlp_engine import SearchEngine


def simulate_user_interactions():
    """Simula algumas interações do usuário com feedback"""
    print("🎭 SIMULANDO INTERAÇÕES DO USUÁRIO")
    print("=" * 50)
    
    # Inicializa componentes
    search_engine = SearchEngine()
    feedback_repo = FeedbackRepository()
    
    if not search_engine.is_available():
        print("⚠️ Modelo NLP não disponível. Simulação limitada.")
        return
    
    # Simulações de perguntas e feedbacks
    interactions = [
        {
            "question": "Como pedir férias?",
            "feedback": True,  # Thumbs up
            "comment": "Usuário satisfeito com a resposta"
        },
        {
            "question": "Qual o horário de funcionamento?", 
            "feedback": True,  # Thumbs up
            "comment": "Resposta clara e útil"
        },
        {
            "question": "Como funciona o home office?",
            "feedback": False,  # Thumbs down
            "comment": "Resposta não foi clara o suficiente"
        },
        {
            "question": "Onde fica o refeitório?",
            "feedback": True,  # Thumbs up
            "comment": "Informação precisa"
        },
        {
            "question": "Como reportar problemas técnicos?",
            "feedback": False,  # Thumbs down
            "comment": "Faltaram detalhes na resposta"
        }
    ]
    
    print(f"Simulando {len(interactions)} interações...\n")
    
    for i, interaction in enumerate(interactions, 1):
        question = interaction["question"]
        is_positive = interaction["feedback"]
        comment = interaction["comment"]
        
        print(f"{i}. Pergunta: '{question}'")
        
        # Busca resposta
        results = search_engine.search(question, top_k=1)
        
        if results:
            result = results[0]
            faq_id = result.faq.id
            confidence = result.confidence
            
            print(f"   Resposta encontrada: FAQ #{faq_id}")
            print(f"   Confiança: {confidence:.1%}")
            
            # Simula feedback do usuário
            feedback_icon = "👍" if is_positive else "👎"
            print(f"   Feedback simulado: {feedback_icon} ({comment})")
            
            # Salva feedback no banco
            try:
                user_embedding = search_engine.generate_embedding(question)
                feedback = feedback_repo.create_feedback(
                    user_question=question,
                    faq_id=faq_id,
                    is_positive=is_positive,
                    confidence_score=confidence,
                    user_question_embedding=user_embedding
                )
                print(f"   ✅ Feedback salvo: ID #{feedback.id}")
                
            except Exception as e:
                print(f"   ❌ Erro ao salvar feedback: {e}")
        else:
            print("   ❌ Nenhuma resposta encontrada")
        
        print()
    
    return len(interactions)


def show_feedback_summary():
    """Mostra resumo dos feedbacks após simulação"""
    print("📊 RESUMO DOS FEEDBACKS")
    print("=" * 50)
    
    feedback_repo = FeedbackRepository()
    stats = feedback_repo.get_feedback_stats()
    
    print(f"Total de feedbacks: {stats['total']}")
    print(f"Feedbacks positivos: {stats['positive']} ({stats['positive_rate']:.1f}%)")
    print(f"Feedbacks negativos: {stats['negative']} ({stats['negative_rate']:.1f}%)")
    
    if stats['total'] > 0:
        print(f"\n📈 Taxa de satisfação geral: {stats['positive_rate']:.1f}%")
        
        # Mostra FAQs problemáticas
        problematic = feedback_repo.get_problematic_faqs(min_negative_feedback=1)
        if problematic:
            print(f"\n🚨 FAQs que precisam de atenção:")
            for item in problematic:
                faq = item['faq']
                negative_rate = item['negative_rate']
                print(f"  • FAQ #{faq.id}: {negative_rate:.1f}% negativos")
                print(f"    '{faq.question[:60]}...'")


def main():
    """Função principal da demonstração"""
    print("=" * 60)
    print("  DEMONSTRAÇÃO DO SISTEMA DE FEEDBACK")
    print("  Assistente Corporativo")
    print("=" * 60)
    print()
    
    try:
        # Inicializa banco
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        Base.metadata.create_all(engine)
        
        # Verifica se há FAQs no banco
        faq_repo = FAQRepository()
        faq_count = faq_repo.count()
        
        if faq_count == 0:
            print("❌ Nenhuma FAQ encontrada no banco!")
            print("💡 Execute primeiro: python add_sample_data.py")
            return 1
        
        print(f"✅ Encontradas {faq_count} FAQs no banco")
        print()
        
        # Simula interações
        interactions_count = simulate_user_interactions()
        
        if interactions_count > 0:
            print()
            show_feedback_summary()
            
            print("\n" + "=" * 60)
            print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
            print(f"📊 {interactions_count} interações simuladas com sucesso")
            print("🔍 Use 'python view_feedback_stats.py' para análise detalhada")
            print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())