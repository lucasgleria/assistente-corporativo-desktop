"""
Debug do sistema de penalidades
"""

import sys
import os
import numpy as np

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.models import Base, DynamicPenalty
from app.database.repository import DynamicPenaltyRepository

def test_penalty_creation():
    """Testa criação de penalidade"""
    print("🔍 DEBUGANDO CRIAÇÃO DE PENALIDADE")
    print("=" * 50)
    
    try:
        # Inicializa banco
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        Base.metadata.create_all(engine)
        
        # Cria embedding de teste
        test_embedding = np.random.rand(384).astype(np.float32)
        print(f"✓ Embedding criado: shape={test_embedding.shape}, dtype={test_embedding.dtype}")
        
        # Testa criação direta
        print("\n1. Testando criação direta...")
        penalty = DynamicPenalty(
            1,  # faq_id
            test_embedding,  # user_question_embedding
            "Teste de pergunta",  # original_question
            0.5,  # penalty_factor
            0.8   # similarity_radius
        )
        
        print(f"✓ Objeto criado")
        print(f"  - faq_id: {penalty.faq_id}")
        print(f"  - question_embedding: {type(penalty.question_embedding)}")
        print(f"  - original_question: {penalty.original_question}")
        print(f"  - penalty_factor: {penalty.penalty_factor}")
        
        # Testa salvamento
        print("\n2. Testando salvamento no banco...")
        with db_manager.get_session() as session:
            session.add(penalty)
            session.commit()
            print(f"✓ Penalidade salva com ID: {penalty.id}")
        
        # Testa repositório
        print("\n3. Testando repositório...")
        repo = DynamicPenaltyRepository()
        penalty2 = repo.create_penalty(
            faq_id=2,
            question_embedding=test_embedding,
            original_question="Teste via repositório",
            penalty_factor=0.3
        )
        print(f"✓ Penalidade via repositório: ID={penalty2.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_penalty_creation()