"""
Repositório para operações CRUD abstratas
Implementa padrão Repository para isolar a lógica de acesso a dados
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Integer
import numpy as np

from app.database.connection import get_db_session, get_db_transaction
from app.database.models import FAQ, SearchResult, UserFeedback, DynamicPenalty
from app.config import NLP_CONFIG


class FAQRepository:
    """
    Repositório para operações com FAQs
    Implementa CRUD completo e busca por similaridade
    """
    
    def __init__(self):
        """Inicializa o repositório"""
        self.similarity_threshold = NLP_CONFIG['similarity_threshold']
    
    def create(self, question: str, answer: str, embedding: Optional[np.ndarray] = None) -> FAQ:
        """
        Cria uma nova FAQ
        
        Args:
            question: Pergunta
            answer: Resposta
            embedding: Embedding da pergunta (opcional)
            
        Returns:
            FAQ criada
            
        Raises:
            SQLAlchemyError: Erro ao salvar no banco
        """
        try:
            with get_db_transaction() as session:
                faq = FAQ(question=question, answer=answer, embedding=embedding)
                session.add(faq)
                session.flush()  # Para obter o ID antes do commit
                return faq
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao criar FAQ: {e}")
            raise
        except Exception as e:
            print(f"✗ Erro inesperado ao criar FAQ: {e}")
            raise
    
    def get_by_id(self, faq_id: int) -> Optional[FAQ]:
        """
        Busca FAQ por ID
        
        Args:
            faq_id: ID da FAQ
            
        Returns:
            FAQ encontrada ou None
        """
        try:
            with get_db_session() as session:
                return session.query(FAQ).filter(FAQ.id == faq_id).first()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar FAQ por ID: {e}")
            return None
    
    def get_all(self, limit: Optional[int] = None) -> List[FAQ]:
        """
        Busca todas as FAQs
        
        Args:
            limit: Limite de resultados (opcional)
            
        Returns:
            Lista de FAQs
        """
        try:
            with get_db_session() as session:
                query = session.query(FAQ).order_by(FAQ.created_at.desc())
                
                if limit:
                    query = query.limit(limit)
                
                return query.all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar todas as FAQs: {e}")
            return []
    
    def get_with_embeddings(self) -> List[FAQ]:
        """
        Busca apenas FAQs que possuem embeddings
        
        Returns:
            Lista de FAQs com embeddings
        """
        try:
            with get_db_session() as session:
                return session.query(FAQ).filter(FAQ.embedding.isnot(None)).all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar FAQs com embeddings: {e}")
            return []
    
    def update(self, faq_id: int, **kwargs) -> Optional[FAQ]:
        """
        Atualiza uma FAQ
        
        Args:
            faq_id: ID da FAQ
            **kwargs: Campos a serem atualizados
            
        Returns:
            FAQ atualizada ou None se não encontrada
        """
        try:
            with get_db_transaction() as session:
                faq = session.query(FAQ).filter(FAQ.id == faq_id).first()
                
                if not faq:
                    return None
                
                # Atualiza apenas campos válidos
                valid_fields = ['question', 'answer', 'embedding']
                for field, value in kwargs.items():
                    if field in valid_fields:
                        setattr(faq, field, value)
                
                return faq
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao atualizar FAQ: {e}")
            return None
    
    def delete(self, faq_id: int) -> bool:
        """
        Remove uma FAQ
        
        Args:
            faq_id: ID da FAQ
            
        Returns:
            True se removida com sucesso, False caso contrário
        """
        try:
            with get_db_transaction() as session:
                faq = session.query(FAQ).filter(FAQ.id == faq_id).first()
                
                if not faq:
                    return False
                
                session.delete(faq)
                return True
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao remover FAQ: {e}")
            return False
    
    def count(self) -> int:
        """
        Conta o número total de FAQs
        
        Returns:
            Número de FAQs no banco
        """
        try:
            with get_db_session() as session:
                return session.query(FAQ).count()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao contar FAQs: {e}")
            return 0
    
    def search_by_text(self, query: str, limit: int = 10) -> List[FAQ]:
        """
        Busca FAQs por texto (busca simples)
        
        Args:
            query: Texto a buscar
            limit: Limite de resultados
            
        Returns:
            Lista de FAQs que contêm o texto
        """
        try:
            with get_db_session() as session:
                return session.query(FAQ).filter(
                    FAQ.question.contains(query) | FAQ.answer.contains(query)
                ).limit(limit).all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro na busca por texto: {e}")
            return []
    
    def search_by_similarity(self, query_embedding: np.ndarray, 
                           top_k: int = 1, 
                           threshold: Optional[float] = None,
                           apply_penalties: bool = True) -> List[SearchResult]:
        """
        Busca FAQs por similaridade de embedding com penalidades dinâmicas
        
        Args:
            query_embedding: Embedding da pergunta do usuário
            top_k: Número máximo de resultados
            threshold: Limite mínimo de similaridade (usa config se None)
            apply_penalties: Se deve aplicar penalidades dinâmicas
            
        Returns:
            Lista de SearchResult ordenada por similaridade (com penalidades aplicadas)
        """
        if threshold is None:
            threshold = self.similarity_threshold
        
        try:
            # Busca todas as FAQs com embeddings
            faqs_with_embeddings = self.get_with_embeddings()
            
            if not faqs_with_embeddings:
                return []
            
            # Busca penalidades ativas se necessário
            penalty_repo = None
            if apply_penalties:
                from app.database.repository import DynamicPenaltyRepository
                penalty_repo = DynamicPenaltyRepository()
            
            results = []
            
            for faq in faqs_with_embeddings:
                if faq.embedding is not None:
                    # Calcula similaridade de cosseno
                    base_similarity = self._cosine_similarity(query_embedding, faq.embedding)
                    
                    # Aplica penalidades dinâmicas se habilitado
                    final_similarity = base_similarity
                    if apply_penalties and penalty_repo:
                        penalty_factor = penalty_repo.calculate_penalty_for_question(
                            faq.id, query_embedding
                        )
                        final_similarity = base_similarity * penalty_factor
                        
                        # Log para debug se penalidade foi aplicada
                        if penalty_factor < 1.0:
                            print(f"🚫 Penalidade aplicada: FAQ #{faq.id} "
                                  f"({base_similarity:.3f} → {final_similarity:.3f})")
                    
                    # Adiciona apenas se passar no threshold (após penalidades)
                    if final_similarity >= threshold:
                        results.append(SearchResult(faq, final_similarity))
            
            # Ordena por similaridade final (maior primeiro) e limita resultados
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"✗ Erro na busca por similaridade: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcula similaridade de cosseno entre dois vetores
        
        Args:
            vec1: Primeiro vetor
            vec2: Segundo vetor
            
        Returns:
            Similaridade de cosseno (0.0 a 1.0)
        """
        try:
            # Normaliza os vetores
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calcula produto escalar (similaridade de cosseno)
            similarity = np.dot(vec1_norm, vec2_norm)
            
            # Garante que o resultado esteja entre 0 e 1
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            print(f"✗ Erro ao calcular similaridade de cosseno: {e}")
            return 0.0
    
    def bulk_create(self, faqs_data: List[Dict[str, Any]]) -> List[FAQ]:
        """
        Cria múltiplas FAQs em lote
        
        Args:
            faqs_data: Lista de dicionários com dados das FAQs
            
        Returns:
            Lista de FAQs criadas
        """
        try:
            with get_db_transaction() as session:
                faqs = []
                
                for data in faqs_data:
                    faq = FAQ(
                        question=data['question'],
                        answer=data['answer'],
                        embedding=data.get('embedding')
                    )
                    faqs.append(faq)
                    session.add(faq)
                
                session.flush()  # Para obter os IDs
                return faqs
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao criar FAQs em lote: {e}")
            raise
    
    def update_embeddings(self, embeddings_map: Dict[int, np.ndarray]) -> int:
        """
        Atualiza embeddings de múltiplas FAQs
        
        Args:
            embeddings_map: Mapeamento {faq_id: embedding}
            
        Returns:
            Número de FAQs atualizadas
        """
        updated_count = 0
        
        try:
            with get_db_transaction() as session:
                for faq_id, embedding in embeddings_map.items():
                    faq = session.query(FAQ).filter(FAQ.id == faq_id).first()
                    if faq:
                        faq.embedding = embedding
                        updated_count += 1
                
                return updated_count
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao atualizar embeddings: {e}")
            return 0


class FeedbackRepository:
    """
    Repositório para operações com feedback do usuário
    Gerencia dados de treinamento para melhoria do modelo
    """
    
    def __init__(self):
        """Inicializa o repositório de feedback"""
        pass
    
    def create_feedback(self, user_question: str, faq_id: int, is_positive: bool,
                       confidence_score: float = 0.0, 
                       user_question_embedding: Optional[np.ndarray] = None) -> UserFeedback:
        """
        Cria um novo feedback do usuário
        
        Args:
            user_question: Pergunta original do usuário
            faq_id: ID da FAQ que foi avaliada
            is_positive: True para thumbs up, False para thumbs down
            confidence_score: Score de confiança da resposta
            user_question_embedding: Embedding da pergunta do usuário
            
        Returns:
            UserFeedback criado
        """
        try:
            with get_db_transaction() as session:
                feedback = UserFeedback(
                    user_question=user_question,
                    faq_id=faq_id,
                    is_positive=is_positive,
                    confidence_score=confidence_score,
                    user_question_embedding=user_question_embedding
                )
                session.add(feedback)
                session.flush()
                
                feedback_type = "👍 Positivo" if is_positive else "👎 Negativo"
                print(f"✓ Feedback registrado: {feedback_type} para FAQ #{faq_id}")
                
                return feedback
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao criar feedback: {e}")
            raise
    
    def get_feedback_by_faq(self, faq_id: int) -> List[UserFeedback]:
        """
        Busca todos os feedbacks para uma FAQ específica
        
        Args:
            faq_id: ID da FAQ
            
        Returns:
            Lista de feedbacks para a FAQ
        """
        try:
            with get_db_session() as session:
                return session.query(UserFeedback).filter(
                    UserFeedback.faq_id == faq_id
                ).order_by(UserFeedback.created_at.desc()).all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar feedback por FAQ: {e}")
            return []
    
    def get_all_feedback(self, limit: Optional[int] = None) -> List[UserFeedback]:
        """
        Busca todos os feedbacks
        
        Args:
            limit: Limite de resultados
            
        Returns:
            Lista de feedbacks
        """
        try:
            with get_db_session() as session:
                query = session.query(UserFeedback).order_by(UserFeedback.created_at.desc())
                
                if limit:
                    query = query.limit(limit)
                
                return query.all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar todos os feedbacks: {e}")
            return []
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas dos feedbacks
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with get_db_session() as session:
                total = session.query(UserFeedback).count()
                positive = session.query(UserFeedback).filter(UserFeedback.is_positive == True).count()
                negative = session.query(UserFeedback).filter(UserFeedback.is_positive == False).count()
                
                return {
                    'total': total,
                    'positive': positive,
                    'negative': negative,
                    'positive_rate': (positive / total * 100) if total > 0 else 0,
                    'negative_rate': (negative / total * 100) if total > 0 else 0
                }
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao calcular estatísticas: {e}")
            return {'total': 0, 'positive': 0, 'negative': 0, 'positive_rate': 0, 'negative_rate': 0}
    
    def get_problematic_faqs(self, min_negative_feedback: int = 2) -> List[Dict[str, Any]]:
        """
        Identifica FAQs com muitos feedbacks negativos
        
        Args:
            min_negative_feedback: Mínimo de feedbacks negativos para considerar problemática
            
        Returns:
            Lista de FAQs problemáticas com estatísticas
        """
        try:
            with get_db_session() as session:
                # Query complexa para contar feedbacks por FAQ
                from sqlalchemy import func
                
                subquery = session.query(
                    UserFeedback.faq_id,
                    func.count(UserFeedback.id).label('total_feedback'),
                    func.sum(func.cast(UserFeedback.is_positive, Integer)).label('positive_count')
                ).group_by(UserFeedback.faq_id).subquery()
                
                results = session.query(
                    FAQ,
                    subquery.c.total_feedback,
                    subquery.c.positive_count,
                    (subquery.c.total_feedback - subquery.c.positive_count).label('negative_count')
                ).join(subquery, FAQ.id == subquery.c.faq_id).filter(
                    (subquery.c.total_feedback - subquery.c.positive_count) >= min_negative_feedback
                ).all()
                
                problematic_faqs = []
                for faq, total, positive, negative in results:
                    problematic_faqs.append({
                        'faq': faq,
                        'total_feedback': total,
                        'positive_feedback': positive or 0,
                        'negative_feedback': negative,
                        'negative_rate': (negative / total * 100) if total > 0 else 0
                    })
                
                return problematic_faqs
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar FAQs problemáticas: {e}")
            return []
    
    def delete_feedback(self, feedback_id: int) -> bool:
        """
        Remove um feedback
        
        Args:
            feedback_id: ID do feedback
            
        Returns:
            True se removido com sucesso
        """
        try:
            with get_db_transaction() as session:
                feedback = session.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
                
                if not feedback:
                    return False
                
                session.delete(feedback)
                return True
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao remover feedback: {e}")
            return False
    
    def count(self) -> int:
        """
        Conta o número total de feedbacks
        
        Returns:
            Número de feedbacks no banco
        """
        try:
            with get_db_session() as session:
                return session.query(UserFeedback).count()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao contar feedbacks: {e}")
            return 0


class DynamicPenaltyRepository:
    """
    Repositório para penalidades dinâmicas
    Gerencia aprendizado em tempo real baseado em feedback negativo
    """
    
    def __init__(self):
        """Inicializa o repositório de penalidades"""
        pass
    
    def create_penalty(self, faq_id: int, question_embedding: np.ndarray, 
                      original_question: str, penalty_factor: float = 0.3,
                      similarity_radius: float = 0.85) -> DynamicPenalty:
        """
        Cria uma nova penalidade dinâmica
        
        Args:
            faq_id: ID da FAQ a ser penalizada
            question_embedding: Embedding da pergunta que causou feedback negativo
            original_question: Pergunta original
            penalty_factor: Fator de penalidade (0.0 = bloqueia, 1.0 = sem penalidade)
            similarity_radius: Raio de similaridade para aplicar penalidade
            
        Returns:
            DynamicPenalty criada
        """
        try:
            with get_db_transaction() as session:
                penalty = DynamicPenalty(
                    faq_id=faq_id,
                    user_question_embedding=question_embedding,
                    original_question=original_question,
                    penalty_factor=penalty_factor,
                    similarity_radius=similarity_radius
                )
                session.add(penalty)
                session.flush()
                
                print(f"🚫 Penalidade criada: FAQ #{faq_id} reduzida em {(1-penalty_factor)*100:.0f}%")
                return penalty
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao criar penalidade: {e}")
            raise
    
    def get_active_penalties(self) -> List[DynamicPenalty]:
        """
        Busca todas as penalidades ativas (não expiradas)
        
        Returns:
            Lista de penalidades ativas
        """
        try:
            with get_db_session() as session:
                from datetime import datetime
                
                # Busca penalidades que não expiraram
                penalties = session.query(DynamicPenalty).filter(
                    (DynamicPenalty.expires_at.is_(None)) |
                    (DynamicPenalty.expires_at > datetime.utcnow())
                ).all()
                
                return penalties
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar penalidades ativas: {e}")
            return []
    
    def get_penalties_for_faq(self, faq_id: int) -> List[DynamicPenalty]:
        """
        Busca penalidades para uma FAQ específica
        
        Args:
            faq_id: ID da FAQ
            
        Returns:
            Lista de penalidades para a FAQ
        """
        try:
            with get_db_session() as session:
                return session.query(DynamicPenalty).filter(
                    DynamicPenalty.faq_id == faq_id
                ).order_by(DynamicPenalty.created_at.desc()).all()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao buscar penalidades da FAQ: {e}")
            return []
    
    def calculate_penalty_for_question(self, faq_id: int, question_embedding: np.ndarray) -> float:
        """
        Calcula o fator de penalidade total para uma FAQ em relação a uma pergunta
        
        Args:
            faq_id: ID da FAQ
            question_embedding: Embedding da pergunta
            
        Returns:
            Fator de penalidade (0.0 = bloqueado, 1.0 = sem penalidade)
        """
        try:
            penalties = self.get_penalties_for_faq(faq_id)
            
            if not penalties:
                return 1.0  # Sem penalidade
            
            # Encontra a maior penalidade aplicável
            max_penalty = 1.0
            
            for penalty in penalties:
                if penalty.applies_to_question(question_embedding):
                    max_penalty = min(max_penalty, penalty.penalty_factor)
            
            return max_penalty
            
        except Exception as e:
            print(f"✗ Erro ao calcular penalidade: {e}")
            return 1.0  # Em caso de erro, não aplica penalidade
    
    def cleanup_expired_penalties(self) -> int:
        """
        Remove penalidades expiradas do banco
        
        Returns:
            Número de penalidades removidas
        """
        try:
            with get_db_transaction() as session:
                from datetime import datetime
                
                # Remove penalidades expiradas
                deleted_count = session.query(DynamicPenalty).filter(
                    DynamicPenalty.expires_at.isnot(None),
                    DynamicPenalty.expires_at <= datetime.utcnow()
                ).delete()
                
                if deleted_count > 0:
                    print(f"🧹 {deleted_count} penalidades expiradas removidas")
                
                return deleted_count
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao limpar penalidades expiradas: {e}")
            return 0
    
    def remove_penalty(self, penalty_id: int) -> bool:
        """
        Remove uma penalidade específica
        
        Args:
            penalty_id: ID da penalidade
            
        Returns:
            True se removida com sucesso
        """
        try:
            with get_db_transaction() as session:
                penalty = session.query(DynamicPenalty).filter(
                    DynamicPenalty.id == penalty_id
                ).first()
                
                if not penalty:
                    return False
                
                session.delete(penalty)
                print(f"🗑️ Penalidade #{penalty_id} removida")
                return True
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao remover penalidade: {e}")
            return False
    
    def get_penalty_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das penalidades
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with get_db_session() as session:
                from datetime import datetime
                
                total = session.query(DynamicPenalty).count()
                active = session.query(DynamicPenalty).filter(
                    (DynamicPenalty.expires_at.is_(None)) |
                    (DynamicPenalty.expires_at > datetime.utcnow())
                ).count()
                expired = total - active
                
                # FAQs mais penalizadas
                from sqlalchemy import func
                most_penalized = session.query(
                    DynamicPenalty.faq_id,
                    func.count(DynamicPenalty.id).label('penalty_count')
                ).group_by(DynamicPenalty.faq_id).order_by(
                    func.count(DynamicPenalty.id).desc()
                ).limit(5).all()
                
                return {
                    'total_penalties': total,
                    'active_penalties': active,
                    'expired_penalties': expired,
                    'most_penalized_faqs': [
                        {'faq_id': faq_id, 'penalty_count': count}
                        for faq_id, count in most_penalized
                    ]
                }
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao calcular estatísticas de penalidades: {e}")
            return {
                'total_penalties': 0,
                'active_penalties': 0,
                'expired_penalties': 0,
                'most_penalized_faqs': []
            }
    
    def count(self) -> int:
        """
        Conta o número total de penalidades
        
        Returns:
            Número de penalidades no banco
        """
        try:
            with get_db_session() as session:
                return session.query(DynamicPenalty).count()
                
        except SQLAlchemyError as e:
            print(f"✗ Erro ao contar penalidades: {e}")
            return 0