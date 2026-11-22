"""
Script de exemplo para adicionar dados ao assistente corporativo
Execute este script para popular o banco com perguntas/respostas de exemplo
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import DatabaseManager
from app.database.models import Base, FAQ
from app.database.repository import FAQRepository
from app.core.nlp_engine import SearchEngine


def create_sample_data():
    """Cria dados de exemplo para demonstração"""
    
    sample_faqs = [
        {
            "question": "Como faço para solicitar férias?",
            "answer": "Para solicitar férias, siga estes passos:\n\n1. Acesse o sistema RH interno (portal.empresa.com)\n2. Vá em 'Solicitações' > 'Férias'\n3. Preencha o formulário com as datas desejadas\n4. Anexe justificativa se necessário\n5. Envie para aprovação do gestor\n\nLembre-se: solicite com pelo menos 30 dias de antecedência."
        },
        {
            "question": "Qual é a política de home office da empresa?",
            "answer": "Nossa política de home office permite:\n\n• Até 2 dias por semana em casa\n• Aprovação prévia do gestor direto\n• Equipamentos adequados (notebook, internet estável)\n• Disponibilidade durante horário comercial\n• Participação em reuniões obrigatórias\n\nPara solicitar, use o formulário no portal RH ou fale com seu gestor."
        },
        {
            "question": "Como reportar problemas técnicos?",
            "answer": "Para reportar problemas técnicos:\n\n📧 Email: suporte@empresa.com\n🎫 Sistema de tickets: helpdesk.empresa.com\n📞 Telefone: (11) 1234-5678 (ramal 100)\n\nSempre inclua:\n• Descrição detalhada do problema\n• Prints de tela se possível\n• Seu nome e setor\n• Urgência (baixa/média/alta)\n\nTempo de resposta: até 4h para problemas críticos."
        },
        {
            "question": "Onde encontro o manual do funcionário?",
            "answer": "O manual do funcionário está disponível em:\n\n🌐 Portal interno: portal.empresa.com/manual\n📁 Pasta compartilhada: \\\\servidor\\RH\\Manuais\n📱 App móvel da empresa (seção 'Documentos')\n\nO manual contém:\n• Políticas da empresa\n• Benefícios\n• Código de conduta\n• Procedimentos internos\n\nVersão atualizada: Janeiro 2024"
        },
        {
            "question": "Como funciona o plano de saúde?",
            "answer": "Nosso plano de saúde oferece:\n\n🏥 Cobertura nacional\n👨‍⚕️ Rede credenciada ampla\n💊 Farmácia com desconto\n🦷 Odontológico incluso\n👁️ Oftalmológico básico\n\nPara usar:\n• Apresente a carteirinha\n• Consultas: agendamento direto\n• Exames: autorização prévia\n• Emergências: cobertura 24h\n\nDúvidas: rh@empresa.com ou ramal 200"
        },
        {
            "question": "Qual o horário de funcionamento?",
            "answer": "Horários de funcionamento:\n\n🕘 Segunda a Quinta: 8h às 18h\n🕘 Sexta-feira: 8h às 17h\n🕘 Almoço: 12h às 13h (flexível)\n\nModalidades:\n• Horário fixo: entrada/saída fixas\n• Horário flexível: ±1h de tolerância\n• Banco de horas: compensação mensal\n\nControle de ponto: cartão ou biometria na recepção."
        },
        {
            "question": "Como solicitar reembolso de despesas?",
            "answer": "Para reembolso de despesas corporativas:\n\n📋 Procedimento:\n1. Guarde todos os recibos/notas fiscais\n2. Preencha o formulário de reembolso\n3. Anexe comprovantes digitalizados\n4. Envie para aprovação do gestor\n5. Aguarde processamento (até 15 dias)\n\n💰 Itens reembolsáveis:\n• Transporte a trabalho\n• Hospedagem em viagens\n• Alimentação (limite R$ 50/dia)\n• Material de escritório aprovado\n\nFormulário: portal.empresa.com/reembolso"
        },
        {
            "question": "Onde fica o refeitório?",
            "answer": "Localização do refeitório:\n\n📍 2º andar, ala oeste\n🕐 Funcionamento: 11h30 às 14h30\n\n🍽️ Opções disponíveis:\n• Prato executivo (R$ 15,00)\n• Saladas e grelhados (R$ 12,00)\n• Lanches rápidos (R$ 5,00 a R$ 8,00)\n• Bebidas e cafés\n\n💳 Pagamento: cartão corporativo ou dinheiro\n📱 Cardápio semanal: app da empresa ou mural"
        },
        {
            "question": "Como acessar a rede Wi-Fi?",
            "answer": "Acesso à rede Wi-Fi corporativa:\n\n📶 Rede: 'EmpresaWiFi'\n🔐 Senha: solicite ao TI (ramal 100)\n\n⚙️ Configuração:\n1. Conecte à rede 'EmpresaWiFi'\n2. Use suas credenciais do sistema\n3. Aceite o certificado de segurança\n\n📱 Para dispositivos pessoais:\n• Rede: 'EmpresaGuest'\n• Acesso limitado (sem sistemas internos)\n• Válido por 24h, renovação automática\n\nProblemas de conexão: contate o suporte técnico."
        },
        {
            "question": "Qual a política de dress code?",
            "answer": "Dress code da empresa:\n\n👔 Segunda a Quinta (Social):\n• Camisa social ou polo\n• Calça social ou jeans escuro\n• Sapato fechado\n• Evitar chinelos, bermudas, regatas\n\n👕 Sexta-feira (Casual):\n• Roupas casuais apropriadas\n• Jeans permitido\n• Tênis liberado\n• Ainda assim, mantenha profissionalismo\n\n🎯 Reuniões externas: sempre social\n🏢 Visitas de clientes: social obrigatório\n\nDúvidas: consulte RH ou seu gestor."
        }
    ]
    
    return sample_faqs


def main():
    """Função principal para adicionar dados"""
    print("=" * 60)
    print("  ADICIONANDO DADOS DE EXEMPLO")
    print("  Assistente Corporativo")
    print("=" * 60)
    print()
    
    try:
        # Inicializa componentes
        print("🔄 Inicializando banco de dados...")
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        # Cria tabelas se não existirem
        Base.metadata.create_all(engine)
        
        # Inicializa repositório e engine NLP
        repo = FAQRepository()
        nlp_engine = SearchEngine()
        
        # Verifica se já existem dados
        existing_count = repo.count()
        print(f"📊 FAQs existentes no banco: {existing_count}")
        
        if existing_count > 0:
            response = input("\n⚠️ Já existem dados no banco. Deseja adicionar mesmo assim? (s/N): ")
            if response.lower() not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada pelo usuário.")
                return 0
        
        # Verifica disponibilidade do modelo NLP
        if not nlp_engine.is_available():
            print("⚠️ Modelo NLP não disponível. Dados serão adicionados sem embeddings.")
            print("   Execute 'python download_model.py' para habilitar busca semântica.")
        
        # Obtém dados de exemplo
        sample_data = create_sample_data()
        print(f"📝 Preparando {len(sample_data)} FAQs de exemplo...")
        
        # Adiciona cada FAQ
        added_count = 0
        for i, faq_data in enumerate(sample_data, 1):
            print(f"🔄 Processando FAQ {i}/{len(sample_data)}: {faq_data['question'][:50]}...")
            
            try:
                # Gera embedding se modelo disponível
                embedding = None
                if nlp_engine.is_available():
                    embedding = nlp_engine.generate_embedding(faq_data['question'])
                
                # Cria FAQ no banco
                faq = repo.create(
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    embedding=embedding
                )
                
                added_count += 1
                print(f"  ✅ FAQ #{faq.id} adicionada com sucesso")
                
            except Exception as e:
                print(f"  ❌ Erro ao adicionar FAQ: {e}")
        
        print()
        print("=" * 60)
        print(f"✅ CONCLUÍDO: {added_count} FAQs adicionadas com sucesso!")
        print(f"📊 Total de FAQs no banco: {repo.count()}")
        
        if nlp_engine.is_available():
            print("🧠 Embeddings gerados para busca semântica")
        else:
            print("⚠️ Embeddings não gerados (modelo NLP indisponível)")
        
        print()
        print("🚀 Agora você pode executar: python main.py")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())