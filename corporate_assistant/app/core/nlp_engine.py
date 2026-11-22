"""
Engine de Processamento de Linguagem Natural
Carrega modelo sentence-transformers localmente e realiza busca por similaridade
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from sentence_transformers import SentenceTransformer
import torch

from app.config import NLP_CONFIG, MODEL_DIR
from app.database.repository import FAQRepository
from app.database.models import SearchResult


class SearchEngine:
    """
    Engine principal para busca semântica usando sentence-transformers
    Funciona completamente offline após o modelo ser baixado
    Implementa padrão Singleton para garantir uma única instância
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa padrão Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializa o engine de busca (apenas uma vez)
        Carrega o modelo do diretório local
        """
        # Evita reinicialização se já foi inicializado
        if SearchEngine._initialized:
            return
            
        self.model: Optional[SentenceTransformer] = None
        self.model_name = NLP_CONFIG['model_name']
        self.model_path = NLP_CONFIG['model_path']
        self.similarity_threshold = NLP_CONFIG['similarity_threshold'] * 0.7  # Reduz threshold para 35%
        self.max_results = NLP_CONFIG['max_results']
        
        # Cache para embeddings (melhora performance)
        self._embedding_cache = {}
        
        # Repositório para acesso aos dados
        self.faq_repository = FAQRepository()
        
        # Sistema de aprendizado em memória (mais simples e confiável)
        self.learning_penalties = {}  # {faq_id: [(question_embedding, penalty_factor)]}
        
        # Inicializa o modelo
        self._load_model()
        
        # Carrega aprendizado salvo automaticamente
        self.auto_load_learning()
        
        # Marca como inicializado
        SearchEngine._initialized = True
        print("🧠 SearchEngine inicializado como Singleton")
    
    def _load_model(self) -> None:
        """
        Carrega o modelo sentence-transformers do diretório local
        
        IMPORTANTE: Para funcionamento offline, o modelo deve ser baixado previamente:
        
        1. Instale: pip install sentence-transformers
        2. Execute este script Python para baixar o modelo:
        
        ```python
        from sentence_transformers import SentenceTransformer
        import os
        
        # Baixa o modelo
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Salva localmente
        model_path = './data/model/all-MiniLM-L6-v2'
        os.makedirs(model_path, exist_ok=True)
        model.save(model_path)
        
        print(f"Modelo salvo em: {model_path}")
        ```
        
        3. Copie os arquivos para o diretório data/model/all-MiniLM-L6-v2/
        """
        try:
            # Verifica se o modelo existe localmente
            if not self.model_path.exists():
                print(f"⚠ Modelo não encontrado em: {self.model_path}")
                print("📋 Para usar offline, baixe o modelo seguindo as instruções no código")
                
                # Tenta carregar do cache do transformers (se disponível)
                try:
                    print("🔄 Tentando carregar modelo do cache...")
                    self.model = SentenceTransformer(self.model_name)
                    print("✓ Modelo carregado do cache")
                except Exception as cache_error:
                    print(f"✗ Erro ao carregar do cache: {cache_error}")
                    print("❌ Modelo não disponível. Funcionalidade de busca desabilitada.")
                    return
            else:
                # Carrega modelo do diretório local
                print(f"🔄 Carregando modelo de: {self.model_path}")
                self.model = SentenceTransformer(str(self.model_path))
                print("✓ Modelo carregado com sucesso do diretório local")
            
            # Configura para CPU se GPU não estiver disponível
            if not torch.cuda.is_available():
                self.model = self.model.to('cpu')
                print("ℹ Usando CPU para inferência (GPU não disponível)")
            else:
                print("✓ Usando GPU para inferência")
                
        except Exception as e:
            print(f"✗ Erro ao carregar modelo NLP: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """
        Verifica se o engine está disponível para uso
        
        Returns:
            True se o modelo foi carregado com sucesso
        """
        return self.model is not None
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Gera embedding para um texto
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Numpy array com o embedding ou None se modelo não disponível
        """
        if not self.is_available():
            print("⚠ Modelo NLP não disponível")
            return None
        
        try:
            # Verifica cache primeiro
            if text in self._embedding_cache:
                return self._embedding_cache[text]
            
            # Gera embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Adiciona ao cache
            self._embedding_cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            print(f"✗ Erro ao gerar embedding: {e}")
            return None
    
    def search(self, query: str, top_k: Optional[int] = None, 
              apply_learning: bool = True) -> List[SearchResult]:
        """
        Busca FAQs similares à pergunta do usuário com aprendizado dinâmico
        
        Args:
            query: Pergunta do usuário
            top_k: Número máximo de resultados (usa config se None)
            apply_learning: Se deve aplicar penalidades de aprendizado
            
        Returns:
            Lista de SearchResult ordenada por similaridade (com aprendizado aplicado)
        """
        if top_k is None:
            top_k = self.max_results
        
        if not self.is_available():
            print("⚠ Busca semântica não disponível (modelo não carregado)")
            return []
        
        try:
            # Gera embedding da pergunta
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Busca normal primeiro
            results = self.faq_repository.search_by_similarity(
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Busca mais resultados para aplicar penalidades
                threshold=self.similarity_threshold,
                apply_penalties=False  # Não usa o sistema antigo
            )
            
            if not results or not apply_learning:
                return results[:top_k]
            
            # Aplica aprendizado em memória
            modified_results = []
            for result in results:
                penalty_factor = self._calculate_penalty_for_faq(result.faq.id, query_embedding)
                new_score = result.similarity_score * penalty_factor
                
                # Log se penalidade foi aplicada
                if penalty_factor < 1.0:
                    print(f"🚫 Penalidade aplicada: FAQ #{result.faq.id} "
                          f"({result.similarity_score:.3f} → {new_score:.3f})")
                
                # Cria novo resultado com score modificado
                modified_result = SearchResult(result.faq, new_score)
                modified_results.append(modified_result)
            
            # Reordena e filtra por threshold
            modified_results.sort(key=lambda x: x.similarity_score, reverse=True)
            final_results = [r for r in modified_results if r.similarity_score >= self.similarity_threshold]
            
            return final_results[:top_k]
            
        except Exception as e:
            print(f"✗ Erro na busca semântica: {e}")
            return []
    
    def get_best_answer(self, query: str) -> Tuple[Optional[str], float]:
        """
        Retorna a melhor resposta para uma pergunta
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Tupla (resposta, confiança) ou (None, 0.0) se não encontrar
        """
        results = self.search(query, top_k=1)
        
        if not results:
            return None, 0.0
        
        best_result = results[0]
        
        # Só retorna se a confiança for suficiente
        if best_result.is_confident(self.similarity_threshold):
            return best_result.answer, best_result.confidence
        
        return None, best_result.confidence
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Gera embeddings para múltiplos textos (mais eficiente)
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings (mesmo tamanho da entrada)
        """
        if not self.is_available():
            return [None] * len(texts)
        
        try:
            # Filtra textos que não estão no cache
            texts_to_process = []
            indices_to_process = []
            
            for i, text in enumerate(texts):
                if text not in self._embedding_cache:
                    texts_to_process.append(text)
                    indices_to_process.append(i)
            
            # Gera embeddings em lote para textos não cacheados
            if texts_to_process:
                new_embeddings = self.model.encode(texts_to_process, convert_to_numpy=True)
                
                # Adiciona ao cache
                for text, embedding in zip(texts_to_process, new_embeddings):
                    self._embedding_cache[text] = embedding
            
            # Monta resultado final
            results = []
            for text in texts:
                results.append(self._embedding_cache.get(text))
            
            return results
            
        except Exception as e:
            print(f"✗ Erro ao gerar embeddings em lote: {e}")
            return [None] * len(texts)
    
    def update_faq_embeddings(self) -> int:
        """
        Atualiza embeddings de todas as FAQs que não possuem
        
        Returns:
            Número de FAQs atualizadas
        """
        if not self.is_available():
            print("⚠ Não é possível atualizar embeddings (modelo não disponível)")
            return 0
        
        try:
            # Busca FAQs sem embeddings
            all_faqs = self.faq_repository.get_all()
            faqs_without_embeddings = [faq for faq in all_faqs if not faq.has_embedding()]
            
            if not faqs_without_embeddings:
                print("✓ Todas as FAQs já possuem embeddings")
                return 0
            
            print(f"🔄 Atualizando embeddings para {len(faqs_without_embeddings)} FAQs...")
            
            # Gera embeddings em lote
            questions = [faq.question for faq in faqs_without_embeddings]
            embeddings = self.batch_generate_embeddings(questions)
            
            # Atualiza no banco
            embeddings_map = {}
            for faq, embedding in zip(faqs_without_embeddings, embeddings):
                if embedding is not None:
                    embeddings_map[faq.id] = embedding
            
            updated_count = self.faq_repository.update_embeddings(embeddings_map)
            print(f"✓ {updated_count} embeddings atualizados")
            
            return updated_count
            
        except Exception as e:
            print(f"✗ Erro ao atualizar embeddings: {e}")
            return 0
    
    def clear_cache(self) -> None:
        """Limpa o cache de embeddings"""
        self._embedding_cache.clear()
        print("✓ Cache de embeddings limpo")
    
    def get_cache_size(self) -> int:
        """Retorna o tamanho do cache"""
        return len(self._embedding_cache)
    
    def apply_negative_feedback(self, user_question: str, faq_id: int, 
                              penalty_factor: float = 0.3) -> bool:
        """
        Aplica feedback negativo criando penalidade em memória
        
        Args:
            user_question: Pergunta que recebeu resposta ruim
            faq_id: ID da FAQ que deve ser penalizada
            penalty_factor: Fator de penalidade (0.0 = bloqueia, 1.0 = sem penalidade)
            
        Returns:
            True se penalidade foi aplicada com sucesso
        """
        if not self.is_available():
            print("⚠️ Não é possível aplicar penalidade (modelo NLP indisponível)")
            return False
        
        try:
            # Gera embedding da pergunta
            question_embedding = self.generate_embedding(user_question)
            if question_embedding is None:
                print("✗ Erro ao gerar embedding para penalidade")
                return False
            
            # Adiciona penalidade em memória
            if faq_id not in self.learning_penalties:
                self.learning_penalties[faq_id] = []
            
            self.learning_penalties[faq_id].append((question_embedding, penalty_factor))
            
            print(f"🎯 Aprendizado aplicado: FAQ #{faq_id} penalizada em {(1-penalty_factor)*100:.0f}% para perguntas similares")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao aplicar feedback negativo: {e}")
            return False
    
    def search_with_learning(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """
        Busca com aprendizado dinâmico aplicado
        
        Args:
            query: Pergunta do usuário
            top_k: Número máximo de resultados
            
        Returns:
            Lista de SearchResult com penalidades aplicadas
        """
        if top_k is None:
            top_k = self.max_results
        
        if not self.is_available():
            print("⚠ Busca com aprendizado não disponível (modelo não carregado)")
            return []
        
        try:
            # Gera embedding da pergunta
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Busca com penalidades aplicadas
            results = self.faq_repository.search_by_similarity(
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=self.similarity_threshold,
                apply_penalties=True  # Aplica aprendizado dinâmico
            )
            
            return results
            
        except Exception as e:
            print(f"✗ Erro na busca com aprendizado: {e}")
            return []
    
    def _calculate_penalty_for_faq(self, faq_id: int, query_embedding: np.ndarray) -> float:
        """
        Calcula penalidade para uma FAQ baseada no aprendizado em memória
        
        Args:
            faq_id: ID da FAQ
            query_embedding: Embedding da pergunta atual
            
        Returns:
            Fator de penalidade (0.0 = bloqueado, 1.0 = sem penalidade)
        """
        if faq_id not in self.learning_penalties:
            return 1.0  # Sem penalidade
        
        max_penalty = 1.0
        
        for penalty_embedding, penalty_factor in self.learning_penalties[faq_id]:
            # Calcula similaridade
            similarity = self._cosine_similarity(query_embedding, penalty_embedding)
            
            # Se a pergunta é similar (>85%), aplica penalidade
            if similarity >= 0.85:
                max_penalty = min(max_penalty, penalty_factor)
        
        return max_penalty
    
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
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            similarity = np.dot(vec1_norm, vec2_norm)
            return max(0.0, min(1.0, float(similarity)))
        except:
            return 0.0
    
    def get_penalty_stats(self) -> dict:
        """
        Retorna estatísticas das penalidades ativas
        
        Returns:
            Dicionário com estatísticas de aprendizado
        """
        try:
            total_penalties = sum(len(penalties) for penalties in self.learning_penalties.values())
            active_faqs = len(self.learning_penalties)
            
            return {
                'learning_enabled': True,
                'total_penalties': total_penalties,
                'penalized_faqs': active_faqs,
                'penalty_threshold': 0.85,
                'system_type': 'in_memory',
                'penalties_detail': {faq_id: len(penalties) for faq_id, penalties in self.learning_penalties.items()}
            }
        except Exception as e:
            print(f"✗ Erro ao obter estatísticas de penalidades: {e}")
            return {'learning_enabled': False}
    
    def debug_penalties(self, query: str) -> None:
        """
        Debug das penalidades para uma pergunta específica
        
        Args:
            query: Pergunta para debugar
        """
        print(f"\n🔍 DEBUG DE PENALIDADES PARA: '{query}'")
        print("-" * 50)
        
        if not self.learning_penalties:
            print("❌ Nenhuma penalidade ativa")
            return
        
        query_embedding = self.generate_embedding(query)
        if query_embedding is None:
            print("❌ Erro ao gerar embedding")
            return
        
        print(f"📊 Total de FAQs penalizadas: {len(self.learning_penalties)}")
        
        for faq_id, penalties in self.learning_penalties.items():
            print(f"\nFAQ #{faq_id}:")
            print(f"  Penalidades: {len(penalties)}")
            
            for i, (penalty_embedding, penalty_factor) in enumerate(penalties, 1):
                similarity = self._cosine_similarity(query_embedding, penalty_embedding)
                will_apply = similarity >= 0.85
                
                print(f"  {i}. Similaridade: {similarity:.3f} | "
                      f"Fator: {penalty_factor:.2f} | "
                      f"Aplica: {'✅' if will_apply else '❌'}")
            
            # Calcula penalidade final
            final_penalty = self._calculate_penalty_for_faq(faq_id, query_embedding)
            print(f"  🎯 Penalidade final: {final_penalty:.3f} ({(1-final_penalty)*100:.0f}% redução)")
    
    def clear_penalties(self) -> None:
        """Limpa todas as penalidades (útil para testes)"""
        self.learning_penalties.clear()
        print("🧹 Todas as penalidades foram limpas")
    
    def save_learning_to_file(self, filepath: Optional[str] = None) -> bool:
        """
        Salva o aprendizado atual em arquivo para persistência entre sessões
        
        Args:
            filepath: Caminho do arquivo (usa padrão se None)
            
        Returns:
            True se salvou com sucesso
        """
        try:
            import pickle
            from pathlib import Path
            
            if filepath is None:
                filepath = Path("data") / "learning_penalties.pkl"
            else:
                filepath = Path(filepath)
            
            # Garante que o diretório existe
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Salva as penalidades
            with open(filepath, 'wb') as f:
                pickle.dump(self.learning_penalties, f)
            
            stats = self.get_penalty_stats()
            print(f"💾 Aprendizado salvo em: {filepath}")
            print(f"   📊 {stats.get('total_penalties', 0)} penalidades salvas")
            print(f"   🎯 {stats.get('penalized_faqs', 0)} FAQs penalizadas")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar aprendizado: {e}")
            return False
    
    def load_learning_from_file(self, filepath: Optional[str] = None) -> bool:
        """
        Carrega aprendizado salvo de arquivo
        
        Args:
            filepath: Caminho do arquivo (usa padrão se None)
            
        Returns:
            True se carregou com sucesso
        """
        try:
            import pickle
            from pathlib import Path
            
            if filepath is None:
                filepath = Path("data") / "learning_penalties.pkl"
            else:
                filepath = Path(filepath)
            
            if not filepath.exists():
                print(f"ℹ️ Arquivo de aprendizado não encontrado: {filepath}")
                return False
            
            # Carrega as penalidades
            with open(filepath, 'rb') as f:
                loaded_penalties = pickle.load(f)
            
            # Valida os dados carregados
            if not isinstance(loaded_penalties, dict):
                print("❌ Formato de arquivo inválido")
                return False
            
            # Aplica as penalidades carregadas
            self.learning_penalties = loaded_penalties
            
            stats = self.get_penalty_stats()
            print(f"📂 Aprendizado carregado de: {filepath}")
            print(f"   📊 {stats.get('total_penalties', 0)} penalidades restauradas")
            print(f"   🎯 {stats.get('penalized_faqs', 0)} FAQs penalizadas")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar aprendizado: {e}")
            return False
    
    def auto_load_learning(self) -> None:
        """Carrega automaticamente o aprendizado salvo (se existir)"""
        try:
            from pathlib import Path
            
            filepath = Path("data") / "learning_penalties.pkl"
            if filepath.exists():
                print("🔄 Carregando aprendizado salvo automaticamente...")
                self.load_learning_from_file()
            else:
                print("ℹ️ Nenhum aprendizado salvo encontrado (primeira execução)")
                
        except Exception as e:
            print(f"⚠️ Erro no carregamento automático: {e}")
    
    def get_learning_file_info(self) -> dict:
        """
        Retorna informações sobre o arquivo de aprendizado
        
        Returns:
            Dicionário com informações do arquivo
        """
        try:
            from pathlib import Path
            import os
            from datetime import datetime
            
            filepath = Path("data") / "learning_penalties.pkl"
            
            if not filepath.exists():
                return {
                    'exists': False,
                    'filepath': str(filepath),
                    'size': 0,
                    'modified': None
                }
            
            stat = filepath.stat()
            
            return {
                'exists': True,
                'filepath': str(filepath),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / 1024 / 1024, 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter informações do arquivo: {e}")
            return {'exists': False, 'error': str(e)}
    
    def get_model_info(self) -> dict:
        """
        Retorna informações sobre o modelo carregado
        
        Returns:
            Dicionário com informações do modelo
        """
        return {
            'model_name': self.model_name,
            'model_path': str(self.model_path),
            'is_available': self.is_available(),
            'similarity_threshold': self.similarity_threshold,
            'max_results': self.max_results,
            'cache_size': self.get_cache_size(),
            'embedding_dimension': NLP_CONFIG['embedding_dimension'],
            'learning_enabled': True,
            'penalty_stats': self.get_penalty_stats()
        }