"""
Modelos ORM para o banco de dados
Usando SQLAlchemy com tipos genéricos para compatibilidade futura com PostgreSQL
"""

from sqlalchemy import Column, Integer, Text, DateTime, PickleType, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import numpy as np
from typing import Optional, List

# Base para todos os modelos
Base = declarative_base()


class FAQ(Base):
    """
    Modelo para perguntas e respostas frequentes
    Inclui embedding para busca por similaridade semântica
    """
    
    __tablename__ = 'faqs'
    
    # Chave primária
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Pergunta original
    question = Column(Text, nullable=False, index=True)
    
    # Resposta correspondente
    answer = Column(Text, nullable=False)
    
    # Embedding da pergunta (vetor numpy serializado)
    # PickleType é compatível com SQLite e PostgreSQL
    embedding = Column(PickleType, nullable=True)
    
    # Metadados de auditoria
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __init__(self, question: str, answer: str, embedding: Optional[np.ndarray] = None):
        """
        Inicializa uma nova FAQ
        
        Args:
            question: Pergunta original
            answer: Resposta correspondente
            embedding: Vetor de embedding (numpy array)
        """
        self.question = question
        self.answer = answer
        self.embedding = embedding
    
    def set_embedding(self, embedding: np.ndarray) -> None:
        """
        Define o embedding da pergunta
        
        Args:
            embedding: Vetor numpy do embedding
        """
        if not isinstance(embedding, np.ndarray):
            raise ValueError("Embedding deve ser um numpy array")
        
        self.embedding = embedding
    
    def get_embedding(self) -> Optional[np.ndarray]:
        """
        Retorna o embedding como numpy array
        
        Returns:
            Numpy array do embedding ou None se não existir
        """
        return self.embedding
    
    def has_embedding(self) -> bool:
        """
        Verifica se a FAQ possui embedding
        
        Returns:
            True se possui embedding, False caso contrário
        """
        return self.embedding is not None
    
    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário
        
        Returns:
            Dicionário com os dados da FAQ
        """
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'has_embedding': self.has_embedding(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        """Representação string do modelo"""
        return f"<FAQ(id={self.id}, question='{self.question[:50]}...', has_embedding={self.has_embedding()})>"
    
    def __str__(self) -> str:
        """String amigável do modelo"""
        return f"FAQ #{self.id}: {self.question[:100]}..."


class UserFeedback(Base):
    """
    Modelo para feedback do usuário sobre respostas
    Usado para treinar e melhorar o sistema
    """
    
    __tablename__ = 'user_feedback'
    
    # Chave primária
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Pergunta original do usuário
    user_question = Column(Text, nullable=False)
    
    # FAQ que foi retornada como resposta
    faq_id = Column(Integer, ForeignKey('faqs.id'), nullable=False)
    
    # Feedback: True = thumbs up, False = thumbs down
    is_positive = Column(Boolean, nullable=False)
    
    # Score de confiança quando a resposta foi dada
    confidence_score = Column(PickleType, nullable=True)  # Float serializado
    
    # Embedding da pergunta do usuário (para análise posterior)
    user_question_embedding = Column(PickleType, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relacionamento com FAQ
    faq = relationship("FAQ", backref="feedbacks")


class DynamicPenalty(Base):
    """
    Modelo para penalidades dinâmicas aplicadas em tempo real
    Reduz score de FAQs que receberam feedback negativo
    """
    
    __tablename__ = 'dynamic_penalties'
    
    # Chave primária
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # FAQ que recebeu penalidade
    faq_id = Column(Integer, ForeignKey('faqs.id'), nullable=False)
    
    # Embedding da pergunta que causou a penalidade
    question_embedding = Column(PickleType, nullable=False)
    
    # Pergunta original (para debug)
    original_question = Column(Text, nullable=False)
    
    # Fator de penalidade (0.0 a 1.0, onde 0.0 = bloqueado completamente)
    penalty_factor = Column(PickleType, nullable=False, default=0.5)  # Float serializado
    
    # Raio de similaridade para aplicar penalidade
    similarity_radius = Column(PickleType, nullable=False, default=0.8)  # Float serializado
    
    # Metadados
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Penalidade pode expirar
    
    # Relacionamento com FAQ
    faq = relationship("FAQ", backref="penalties")
    
    def __init__(self, faq_id: int, user_question_embedding: np.ndarray, original_question: str,
                 penalty_factor: float = 0.5, similarity_radius: float = 0.8, 
                 expires_hours: Optional[int] = None):
        """
        Inicializa uma penalidade dinâmica
        
        Args:
            faq_id: ID da FAQ penalizada
            user_question_embedding: Embedding da pergunta que causou penalidade
            original_question: Pergunta original
            penalty_factor: Fator de redução (0.0 = bloqueia, 0.5 = reduz 50%)
            similarity_radius: Raio de similaridade para aplicar penalidade
            expires_hours: Horas até expirar (None = permanente)
        """
        self.faq_id = faq_id
        self.question_embedding = user_question_embedding
        self.original_question = original_question
        self.penalty_factor = penalty_factor
        self.similarity_radius = similarity_radius
        
        if expires_hours:
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    
    def is_expired(self) -> bool:
        """Verifica se a penalidade expirou"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def applies_to_question(self, question_embedding: np.ndarray) -> bool:
        """
        Verifica se a penalidade se aplica a uma pergunta
        
        Args:
            question_embedding: Embedding da pergunta a verificar
            
        Returns:
            True se a penalidade deve ser aplicada
        """
        if self.is_expired():
            return False
        
        # Calcula similaridade entre embeddings
        similarity = self._cosine_similarity(self.question_embedding, question_embedding)
        return similarity >= self.similarity_radius
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade de cosseno entre dois vetores"""
        try:
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            similarity = np.dot(vec1_norm, vec2_norm)
            return max(0.0, min(1.0, float(similarity)))
        except:
            return 0.0
    
    def to_dict(self) -> dict:
        """Converte penalidade para dicionário"""
        return {
            'id': self.id,
            'faq_id': self.faq_id,
            'original_question': self.original_question,
            'penalty_factor': self.penalty_factor,
            'similarity_radius': self.similarity_radius,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }
    
    def __repr__(self) -> str:
        """Representação string da penalidade"""
        return f"<DynamicPenalty(faq_id={self.faq_id}, penalty={self.penalty_factor}, expired={self.is_expired()})>"
    
    def __str__(self) -> str:
        """String amigável da penalidade"""
        return f"Penalidade FAQ #{self.faq_id}: {(1-self.penalty_factor)*100:.0f}% redução"
    
    def __init__(self, user_question: str, faq_id: int, is_positive: bool, 
                 confidence_score: float = 0.0, user_question_embedding: Optional[np.ndarray] = None):
        """
        Inicializa um feedback do usuário
        
        Args:
            user_question: Pergunta original do usuário
            faq_id: ID da FAQ que foi retornada
            is_positive: True para thumbs up, False para thumbs down
            confidence_score: Score de confiança da resposta
            user_question_embedding: Embedding da pergunta do usuário
        """
        self.user_question = user_question
        self.faq_id = faq_id
        self.is_positive = is_positive
        self.confidence_score = confidence_score
        self.user_question_embedding = user_question_embedding
    
    def to_dict(self) -> dict:
        """
        Converte o feedback para dicionário
        
        Returns:
            Dicionário com os dados do feedback
        """
        return {
            'id': self.id,
            'user_question': self.user_question,
            'faq_id': self.faq_id,
            'is_positive': self.is_positive,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'faq_question': self.faq.question if self.faq else None,
            'faq_answer': self.faq.answer if self.faq else None
        }
    
    def __repr__(self) -> str:
        """Representação string do feedback"""
        feedback_type = "👍" if self.is_positive else "👎"
        return f"<UserFeedback(id={self.id}, faq_id={self.faq_id}, feedback={feedback_type})>"
    
    def __str__(self) -> str:
        """String amigável do feedback"""
        feedback_type = "Positivo" if self.is_positive else "Negativo"
        return f"Feedback {feedback_type}: '{self.user_question[:50]}...'"


class SearchResult:
    """
    Classe para resultados de busca por similaridade
    Não é um modelo ORM, apenas uma estrutura de dados
    """
    
    def __init__(self, faq: FAQ, similarity_score: float):
        """
        Inicializa um resultado de busca
        
        Args:
            faq: Instância da FAQ encontrada
            similarity_score: Score de similaridade (0.0 a 1.0)
        """
        self.faq = faq
        self.similarity_score = similarity_score
    
    @property
    def question(self) -> str:
        """Pergunta da FAQ"""
        return self.faq.question
    
    @property
    def answer(self) -> str:
        """Resposta da FAQ"""
        return self.faq.answer
    
    @property
    def confidence(self) -> float:
        """Score de confiança (alias para similarity_score)"""
        return self.similarity_score
    
    def is_confident(self, threshold: float = 0.5) -> bool:
        """
        Verifica se o resultado tem confiança suficiente
        
        Args:
            threshold: Limite mínimo de confiança
            
        Returns:
            True se a confiança for >= threshold
        """
        return self.similarity_score >= threshold
    
    def to_dict(self) -> dict:
        """
        Converte o resultado para dicionário
        
        Returns:
            Dicionário com os dados do resultado
        """
        return {
            'faq': self.faq.to_dict(),
            'similarity_score': self.similarity_score,
            'confidence': self.confidence,
            'is_confident': self.is_confident()
        }
    
    def __repr__(self) -> str:
        """Representação string do resultado"""
        return f"<SearchResult(faq_id={self.faq.id}, score={self.similarity_score:.3f})>"
    
    def __str__(self) -> str:
        """String amigável do resultado"""
        return f"Resultado (confiança: {self.similarity_score:.1%}): {self.faq.question[:50]}..."


# Função utilitária para criar todas as tabelas
def create_all_tables(engine):
    """
    Cria todas as tabelas no banco de dados
    
    Args:
        engine: Engine do SQLAlchemy
    """
    try:
        Base.metadata.create_all(engine)
        print("✓ Tabelas criadas com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        return False


# Função utilitária para dropar todas as tabelas (cuidado!)
def drop_all_tables(engine):
    """
    Remove todas as tabelas do banco de dados
    CUIDADO: Esta operação é irreversível!
    
    Args:
        engine: Engine do SQLAlchemy
    """
    try:
        Base.metadata.drop_all(engine)
        print("⚠ Todas as tabelas foram removidas")
        return True
    except Exception as e:
        print(f"✗ Erro ao remover tabelas: {e}")
        return False