"""
Script para visualizar estatísticas de feedback do usuário
Útil para análise de qualidade das respostas durante desenvolvimento
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.repository import FeedbackRepository, FAQRepository, DynamicPenaltyRepository
from app.database.models import Base


def show_feedback_stats():
    """Mostra estatísticas gerais de feedback"""
    print("📊 ESTATÍSTICAS DE FEEDBACK")
    print("=" * 50)
    
    feedback_repo = FeedbackRepository()
    stats = feedback_repo.get_feedback_stats()
    
    print(f"Total de feedbacks: {stats['total']}")
    print(f"Feedbacks positivos: {stats['positive']} ({stats['positive_rate']:.1f}%)")
    print(f"Feedbacks negativos: {stats['negative']} ({stats['negative_rate']:.1f}%)")
    
    if stats['total'] > 0:
        print(f"\n📈 Taxa de satisfação: {stats['positive_rate']:.1f}%")
        
        if stats['positive_rate'] >= 80:
            print("✅ Excelente! Sistema funcionando bem.")
        elif stats['positive_rate'] >= 60:
            print("⚠️ Bom, mas há espaço para melhorias.")
        else:
            print("❌ Atenção! Muitos feedbacks negativos.")


def show_recent_feedback(limit: int = 10):
    """
    Mostra feedbacks recentes
    
    Args:
        limit: Número de feedbacks a mostrar
    """
    print(f"\n📝 ÚLTIMOS {limit} FEEDBACKS")
    print("=" * 50)
    
    feedback_repo = FeedbackRepository()
    recent_feedbacks = feedback_repo.get_all_feedback(limit=limit)
    
    if not recent_feedbacks:
        print("Nenhum feedback encontrado.")
        return
    
    for i, feedback in enumerate(recent_feedbacks, 1):
        feedback_icon = "👍" if feedback.is_positive else "👎"
        confidence = feedback.confidence_score or 0.0
        
        print(f"\n{i}. {feedback_icon} FAQ #{feedback.faq_id} (Confiança: {confidence:.1%})")
        print(f"   Pergunta: '{feedback.user_question[:60]}...'")
        print(f"   Resposta: '{feedback.faq.answer[:60] if feedback.faq else 'N/A'}...'")
        print(f"   Data: {feedback.created_at.strftime('%d/%m/%Y %H:%M')}")


def show_problematic_faqs():
    """Mostra FAQs com muitos feedbacks negativos"""
    print("\n🚨 FAQs PROBLEMÁTICAS")
    print("=" * 50)
    
    feedback_repo = FeedbackRepository()
    problematic = feedback_repo.get_problematic_faqs(min_negative_feedback=2)
    
    if not problematic:
        print("✅ Nenhuma FAQ problemática encontrada!")
        return
    
    for i, item in enumerate(problematic, 1):
        faq = item['faq']
        negative_rate = item['negative_rate']
        
        print(f"\n{i}. FAQ #{faq.id} - Taxa negativa: {negative_rate:.1f}%")
        print(f"   Pergunta: '{faq.question[:80]}...'")
        print(f"   Feedbacks: {item['positive_feedback']}👍 / {item['negative_feedback']}👎")
        print(f"   💡 Sugestão: Revisar esta resposta")


def show_feedback_by_faq(faq_id: int):
    """
    Mostra todos os feedbacks para uma FAQ específica
    
    Args:
        faq_id: ID da FAQ
    """
    print(f"\n📋 FEEDBACKS PARA FAQ #{faq_id}")
    print("=" * 50)
    
    feedback_repo = FeedbackRepository()
    faq_repo = FAQRepository()
    
    # Busca a FAQ
    faq = faq_repo.get_by_id(faq_id)
    if not faq:
        print(f"❌ FAQ #{faq_id} não encontrada.")
        return
    
    print(f"Pergunta: '{faq.question}'")
    print(f"Resposta: '{faq.answer[:100]}...'")
    
    # Busca feedbacks
    feedbacks = feedback_repo.get_feedback_by_faq(faq_id)
    
    if not feedbacks:
        print("\nNenhum feedback encontrado para esta FAQ.")
        return
    
    print(f"\nTotal de feedbacks: {len(feedbacks)}")
    
    positive_count = sum(1 for f in feedbacks if f.is_positive)
    negative_count = len(feedbacks) - positive_count
    
    print(f"Positivos: {positive_count} ({positive_count/len(feedbacks)*100:.1f}%)")
    print(f"Negativos: {negative_count} ({negative_count/len(feedbacks)*100:.1f}%)")
    
    print("\nDetalhes dos feedbacks:")
    for i, feedback in enumerate(feedbacks, 1):
        feedback_icon = "👍" if feedback.is_positive else "👎"
        confidence = feedback.confidence_score or 0.0
        
        print(f"  {i}. {feedback_icon} Confiança: {confidence:.1%}")
        print(f"     Pergunta do usuário: '{feedback.user_question[:60]}...'")
        print(f"     Data: {feedback.created_at.strftime('%d/%m/%Y %H:%M')}")


def show_learning_stats():
    """Mostra estatísticas do sistema de aprendizado"""
    print("\n🧠 ESTATÍSTICAS DE APRENDIZADO")
    print("=" * 50)
    
    try:
        penalty_repo = DynamicPenaltyRepository()
        stats = penalty_repo.get_penalty_stats()
        
        print(f"Total de penalidades: {stats['total_penalties']}")
        print(f"Penalidades ativas: {stats['active_penalties']}")
        print(f"Penalidades expiradas: {stats['expired_penalties']}")
        
        if stats['active_penalties'] > 0:
            print(f"\n🎯 Sistema está aprendendo ativamente!")
            print(f"   {stats['active_penalties']} FAQs com penalidades aplicadas")
        else:
            print("\n💤 Nenhuma penalidade ativa no momento")
        
        if stats['most_penalized_faqs']:
            print(f"\n🚨 FAQs mais penalizadas:")
            for item in stats['most_penalized_faqs']:
                faq_id = item['faq_id']
                count = item['penalty_count']
                print(f"  • FAQ #{faq_id}: {count} penalidades")
        
        # Mostra penalidades ativas detalhadas
        active_penalties = penalty_repo.get_active_penalties()
        if active_penalties:
            print(f"\n📋 Penalidades ativas detalhadas:")
            for penalty in active_penalties[:5]:  # Mostra apenas as 5 mais recentes
                print(f"  • FAQ #{penalty.faq_id}: {(1-penalty.penalty_factor)*100:.0f}% redução")
                print(f"    Pergunta: '{penalty.original_question[:50]}...'")
                print(f"    Criada: {penalty.created_at.strftime('%d/%m/%Y %H:%M')}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas de aprendizado: {e}")


def export_feedback_data():
    """Exporta dados de feedback e aprendizado para análise"""
    print("\n💾 EXPORTANDO DADOS DE FEEDBACK E APRENDIZADO")
    print("=" * 50)
    
    try:
        import json
        from datetime import datetime
        
        feedback_repo = FeedbackRepository()
        penalty_repo = DynamicPenaltyRepository()
        
        all_feedbacks = feedback_repo.get_all_feedback()
        all_penalties = penalty_repo.get_active_penalties()
        
        # Prepara dados para exportação
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_feedbacks': len(all_feedbacks),
            'total_penalties': len(all_penalties),
            'feedbacks': [],
            'penalties': [],
            'learning_stats': penalty_repo.get_penalty_stats()
        }
        
        # Adiciona feedbacks
        for feedback in all_feedbacks:
            export_data['feedbacks'].append({
                'id': feedback.id,
                'user_question': feedback.user_question,
                'faq_id': feedback.faq_id,
                'faq_question': feedback.faq.question if feedback.faq else None,
                'faq_answer': feedback.faq.answer if feedback.faq else None,
                'is_positive': feedback.is_positive,
                'confidence_score': feedback.confidence_score,
                'created_at': feedback.created_at.isoformat()
            })
        
        # Adiciona penalidades
        for penalty in all_penalties:
            export_data['penalties'].append({
                'id': penalty.id,
                'faq_id': penalty.faq_id,
                'original_question': penalty.original_question,
                'penalty_factor': penalty.penalty_factor,
                'similarity_radius': penalty.similarity_radius,
                'created_at': penalty.created_at.isoformat(),
                'expires_at': penalty.expires_at.isoformat() if penalty.expires_at else None
            })
        
        # Salva arquivo
        export_file = Path("data") / f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados exportados para: {export_file}")
        print(f"📊 Total de {len(all_feedbacks)} feedbacks e {len(all_penalties)} penalidades exportados")
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")


def main():
    """Função principal"""
    print("=" * 60)
    print("  ANÁLISE DE FEEDBACK - ASSISTENTE CORPORATIVO")
    print("=" * 60)
    
    try:
        # Inicializa banco
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        Base.metadata.create_all(engine)
        
        # Menu interativo
        while True:
            print("\n" + "=" * 40)
            print("OPÇÕES DISPONÍVEIS:")
            print("1. Estatísticas gerais")
            print("2. Feedbacks recentes")
            print("3. FAQs problemáticas")
            print("4. Feedback por FAQ específica")
            print("5. Estatísticas de aprendizado")
            print("6. Exportar dados")
            print("0. Sair")
            print("=" * 40)
            
            choice = input("\nEscolha uma opção (0-6): ").strip()
            
            if choice == '0':
                print("👋 Até logo!")
                break
            elif choice == '1':
                show_feedback_stats()
            elif choice == '2':
                try:
                    limit = int(input("Quantos feedbacks mostrar? (padrão: 10): ") or "10")
                    show_recent_feedback(limit)
                except ValueError:
                    show_recent_feedback()
            elif choice == '3':
                show_problematic_faqs()
            elif choice == '4':
                try:
                    faq_id = int(input("Digite o ID da FAQ: "))
                    show_feedback_by_faq(faq_id)
                except ValueError:
                    print("❌ ID inválido. Digite um número.")
            elif choice == '5':
                show_learning_stats()
            elif choice == '6':
                export_feedback_data()
            else:
                print("❌ Opção inválida. Tente novamente.")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())