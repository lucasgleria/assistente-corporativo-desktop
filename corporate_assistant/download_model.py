"""
Script para download do modelo sentence-transformers
Execute este script uma vez para baixar o modelo para uso offline
"""

import os
import sys
from pathlib import Path

def download_model():
    """Baixa o modelo sentence-transformers para uso offline"""
    try:
        print("🔄 Iniciando download do modelo sentence-transformers...")
        
        # Importa sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print("❌ Erro: sentence-transformers não está instalado")
            print("📦 Execute: pip install sentence-transformers")
            return False
        
        # Define caminhos
        model_name = "all-MiniLM-L6-v2"
        model_dir = Path("data/model")
        model_path = model_dir / model_name
        
        # Cria diretório se não existir
        model_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Diretório de destino: {model_path}")
        
        # Verifica se já existe
        if model_path.exists() and any(model_path.iterdir()):
            print("✅ Modelo já existe no diretório local")
            return True
        
        # Baixa o modelo
        print(f"⬇️ Baixando modelo '{model_name}'...")
        print("   Isso pode levar alguns minutos na primeira vez...")
        
        model = SentenceTransformer(model_name)
        
        # Salva localmente
        print(f"💾 Salvando modelo em: {model_path}")
        model.save(str(model_path))
        
        # Testa o modelo
        print("🧪 Testando modelo...")
        test_embedding = model.encode("Teste de funcionamento")
        print(f"✅ Modelo funcionando! Dimensão do embedding: {len(test_embedding)}")
        
        print("🎉 Download concluído com sucesso!")
        print(f"📂 Modelo salvo em: {model_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o download: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("  DOWNLOAD DO MODELO SENTENCE-TRANSFORMERS")
    print("  Assistente Corporativo - Modo Offline")
    print("=" * 60)
    print()
    
    # Verifica se está no diretório correto
    if not Path("main.py").exists():
        print("⚠️ Execute este script no diretório raiz do projeto")
        print("   (onde está localizado o arquivo main.py)")
        return 1
    
    # Executa download
    success = download_model()
    
    print()
    if success:
        print("✅ SUCESSO: Modelo baixado e pronto para uso offline!")
        print("🚀 Agora você pode executar: python main.py")
    else:
        print("❌ FALHA: Não foi possível baixar o modelo")
        print("🔧 Verifique sua conexão com a internet e tente novamente")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())