"""
Demonstração simplificada do aprendizado em tempo real
Mostra o conceito funcionando sem as complexidades do ORM
"""

import sys
import os
import numpy as np
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.nlp_engine import SearchEngine

class SimpleLearningSystem:
    """Sistema de aprendizado simplificado em memória"""
    
    def __init__(self):
        self.penalties = {}  # {faq_id: [(question_embedding, penalty_factor)]}
        self.search_engine = SearchEngine()
    
    def add_penalty(self, faq_id: int, question_embedding: np.ndarray, penalty_factor: float = 0.3):
        """Adiciona penalidade para uma FAQ"""
        if faq_id not in self.penalties:
            self.penalties[faq_id] = []
        
        self.penalties[faq_id].append((question_embedding, penalty_factor))
        print(f"🚫 Penalidade adicionada: FAQ #{faq_id} reduzida em {(1-penalty_factor)*100:.0f}%")
    
    def calculate_penalty(self, faq_id: int, query_embedding: np.ndarray) -> float:
        """Calcula penalidade para uma FAQ baseada na pergunta"""
        if faq_id not in self.penalties:
            return 1.0  # Sem penalidade
        
        max_penalty = 1.0
        
        for penalty_embedding, penalty_factor in self.penalties[faq_id]:
            # Calcula similaridade
            similarity = self._cosine_similarity(query_embedding, penalty_embedding)
            
            # Se a pergunta é similar (>85%), aplica penalidade
            if similarity >= 0.85:
                max_penalty = min(max_penalty, penalty_factor)
                print(f"🎯 Penalidade aplicada: FAQ #{faq_id} (similaridade: {similarity:.1%})")
        
        return max_penalty
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade de cosseno"""
        try:
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            similarity = np.dot(vec1_norm, vec2_norm)
            return max(0.0, min(1.0, float(similarity)))
        except:
            return 0.0
    
    def search_with_learning(self, query: str, top_k: int = 3):
        """Busca com aprendizado aplicado"""
        if not self.search_engine.is_available():
            return []
        
        # Busca normal primeiro
        results = self.search_engine.search(query, top_k=top_k, apply_learning=False)
        
        if not results:
            return []
        
        # Gera embedding da pergunta
        query_embedding = self.search_engine.generate_embedding(query)
        if query_embedding is None:
            return results
        
        # Aplica penalidades
        modified_results = []
        for result in results:
            penalty_factor = self.calculate_penalty(result.faq.id, query_embedding)
            
            # Cria novo resultado com score modificado
            new_score = result.confidence * penalty_factor
            
            # Cria uma cópia do resultado com novo score
            from app.database.models import SearchResult
            modified_result = SearchResult(result.faq, new_score)
            modified_results.append(modified_result)
        
        # Reordena por novo score
        modified_results.sort(key=lambda x: x.confidence, reverse=True)
        
        return modified_results


def demonstrate_simple_learning():
    """Demonstra o aprendizado simplificado"""
    print("🧠 DEMONSTRAÇÃO DE APRENDIZADO SIMPLIFICADO")
    print("=" * 60)
    
    learning_system = SimpleLearningSystem()
    
    if not learning_system.search_engine.is_available():
        print("❌ Modelo NLP não disponível")
        return False
    
    test_question = "Como pedir férias na empresa?"
    
    print(f"📝 Pergunta de teste: '{test_question}'")
    print()
    
    # 1. Busca inicial
    print("1️⃣ BUSCA INICIAL (sem aprendizado)")
    print("-" * 40)
    
    initial_results = learning_system.search_with_learning(test_question)
    
    if not initial_results:
        print("❌ Nenhum resultado encontrado")
        return False
    
    print("Resultados encontrados:")
    for i, result in enumerate(initial_results, 1):
        print(f"  {i}. FAQ #{result.faq.id}: {result.confidence:.1%} confiança")
        print(f"     '{result.faq.question[:60]}...'")
    
    # Seleciona a melhor para penalizar
    best_faq = initial_results[0].faq.id
    
    print(f"\n🎯 Simulando feedback NEGATIVO para FAQ #{best_faq}")
    print()
    
    # 2. Aplica aprendizado
    print("2️⃣ APLICANDO APRENDIZADO")
    print("-" * 40)
    
    query_embedding = learning_system.search_engine.generate_embedding(test_question)
    learning_system.add_penalty(best_faq, query_embedding, penalty_factor=0.2)
    
    print()
    
    # 3. Busca após aprendizado
    print("3️⃣ BUSCA APÓS APRENDIZADO")
    print("-" * 40)
    
    learned_results = learning_system.search_with_learning(test_question)
    
    print("Resultados após aprendizado:")
    for i, result in enumerate(learned_results, 1):
        print(f"  {i}. FAQ #{result.faq.id}: {result.confidence:.1%} confiança")
        print(f"     '{result.faq.question[:60]}...'")
        
        if result.faq.id == best_faq:
            original_score = initial_results[0].confidence
            print(f"     🚫 PENALIZADA (era {original_score:.1%})")
    
    print()
    
    # 4. Análise
    print("4️⃣ ANÁLISE DO APRENDIZADO")
    print("-" * 40)
    
    initial_best = initial_results[0]
    learned_best = learned_results[0]
    
    if initial_best.faq.id != learned_best.faq.id:
        print("🎉 APRENDIZADO FUNCIONOU!")
        print(f"   Antes: FAQ #{initial_best.faq.id} era a melhor ({initial_best.confidence:.1%})")
        print(f"   Depois: FAQ #{learned_best.faq.id} agora é a melhor ({learned_best.confidence:.1%})")
    else:
        print("ℹ️ A mesma FAQ ainda é a melhor, mas com score reduzido")
        print(f"   Antes: {initial_best.confidence:.1%}")
        print(f"   Depois: {learned_best.confidence:.1%}")
    
    # 5. Teste com pergunta similar
    print("\n5️⃣ TESTE COM PERGUNTA SIMILAR")
    print("-" * 40)
    
    similar_question = "Como solicitar férias?"
    print(f"Pergunta similar: '{similar_question}'")
    
    similar_results = learning_system.search_with_learning(similar_question)
    
    if similar_results:
        best_similar = similar_results[0]
        print(f"Melhor resultado: FAQ #{best_similar.faq.id} ({best_similar.confidence:.1%})")
        
        if best_similar.faq.id == best_faq:
            print("🚫 Penalidade aplicada também para pergunta similar!")
        else:
            print("✅ Pergunta similar não foi afetada pela penalidade")
    
    return True


def main():
    """Função principal"""
    print("=" * 70)
    print("  DEMONSTRAÇÃO DE APRENDIZADO EM TEMPO REAL")
    print("  Versão Simplificada (em memória)")
    print("=" * 70)
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
        
        success = demonstrate_simple_learning()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✨ O conceito de aprendizado em tempo real funciona!")
            print("💡 Próximo passo: implementar persistência no banco")
        else:
            print("❌ Demonstração falhou")
        print("=" * 70)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())