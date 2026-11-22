"""
Gerenciamento de conexão com banco de dados
Implementa padrão Singleton para garantir uma única instância da engine
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import threading

from app.config import get_database_config, ensure_directories


class DatabaseManager:
    """
    Gerenciador de conexão com banco de dados (Singleton)
    Garante uma única instância da engine e sessões thread-safe
    """
    
    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls) -> 'DatabaseManager':
        """Implementa padrão Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o gerenciador apenas uma vez"""
        if self._engine is None:
            self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Inicializa a engine e session factory"""
        try:
            # Garante que os diretórios existam
            ensure_directories()
            
            # Obtém configuração do banco
            db_config = get_database_config()
            
            # Cria engine com configurações específicas
            engine_kwargs = {
                'echo': db_config.get('echo', False),
                'pool_pre_ping': db_config.get('pool_pre_ping', True)
            }
            
            # Adiciona configurações específicas do PostgreSQL se necessário
            if 'postgresql' in db_config['url']:
                engine_kwargs.update({
                    'pool_size': db_config.get('pool_size', 10),
                    'max_overflow': db_config.get('max_overflow', 20)
                })
            
            self._engine = create_engine(db_config['url'], **engine_kwargs)
            
            # Cria session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                expire_on_commit=False
            )
            
            print(f"✓ Conexão com banco estabelecida: {db_config['url']}")
            
        except SQLAlchemyError as e:
            print(f"✗ Erro ao conectar com banco de dados: {e}")
            raise
        except Exception as e:
            print(f"✗ Erro inesperado na inicialização do banco: {e}")
            raise
    
    def get_engine(self) -> Engine:
        """Retorna a engine do banco de dados"""
        if self._engine is None:
            raise RuntimeError("Banco de dados não foi inicializado")
        return self._engine
    
    def get_session(self) -> Session:
        """
        Cria e retorna uma nova sessão do banco
        IMPORTANTE: Sempre use em context manager (with statement)
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory não foi inicializada")
        
        return self._session_factory()
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"✗ Teste de conexão falhou: {e}")
            return False
    
    def close_all_connections(self) -> None:
        """Fecha todas as conexões (útil para shutdown da aplicação)"""
        if self._engine:
            self._engine.dispose()
            print("✓ Conexões com banco fechadas")


# Função utilitária para obter sessão (facilita imports)
def get_db_session() -> Session:
    """
    Função utilitária para obter uma sessão do banco
    Uso: with get_db_session() as session: ...
    """
    db_manager = DatabaseManager()
    return db_manager.get_session()


# Context manager para transações automáticas
class DatabaseTransaction:
    """
    Context manager para transações automáticas
    Faz commit automático ou rollback em caso de erro
    """
    
    def __init__(self):
        self.session: Optional[Session] = None
        self.db_manager = DatabaseManager()
    
    def __enter__(self) -> Session:
        self.session = self.db_manager.get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is None:
                    self.session.commit()
                else:
                    self.session.rollback()
            finally:
                self.session.close()


# Função utilitária para transações
def get_db_transaction() -> DatabaseTransaction:
    """
    Função utilitária para transações automáticas
    Uso: with get_db_transaction() as session: ...
    """
    return DatabaseTransaction()