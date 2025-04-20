# Contabilizei Chatbot 🤖

Um chatbot inteligente desenvolvido com Streamlit e LangGraph para fornecer informações atualizadas sobre os serviços da Contabilizei.

## 🚀 Funcionalidades

- Interface de chat intuitiva e responsiva
- Suporte a múltiplos provedores de LLM (OpenAI e Groq)
- Respostas baseadas em informações atualizadas do site da Contabilizei
- Sistema de agentes especializados para diferentes tipos de interação
- Configuração fácil de chaves de API

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/contabilizei-chatbot.git
cd contabilizei-chatbot
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto com suas chaves de API:
```env
OPENAI_API_KEY=sua_chave_openai
GROQ_API_KEY=sua_chave_groq
```

## 🎮 Como Usar

1. Inicie o aplicativo:
```bash
streamlit run main.py
```

2. Acesse a interface web no navegador (geralmente em http://localhost:8501)

3. Configure suas preferências:
   - Selecione o provedor de LLM desejado (OpenAI ou Groq)
   - Insira sua chave de API correspondente

4. Comece a conversar com o chatbot!

## 🏗️ Estrutura do Projeto

```
Contabilizei_Chatbot/
├── manager/
│   └── agent_manager.py        # Gerencia e delega a execução dos agentes
│
├── agents/
│   ├── welcome_agent.py        # Lida com a saudação inicial e onboarding
│   └── websearch_agent.py      # Realiza buscas no site para responder perguntas
│
├── prompts/
│   ├── welcome.prompt          # Template de prompt para boas-vindas
│   └── websearch.prompt        # Template de prompt para busca na web
│
├── ui/
│   └── streamlit_app.py        # Interface do usuário em Streamlit
│
├── utils/
│   └── webscraper.py           # Funções para buscar e analisar conteúdo do site
│
├── .env                        # Variáveis de ambiente (chaves de API, URLs)
├── requirements.txt            # Dependências do projeto
└── main.py                     # Ponto de entrada da aplicação
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io/) pela incrível framework de UI
- [LangGraph](https://github.com/langchain-ai/langgraph) pela poderosa framework de agentes
- [Contabilizei](https://www.contabilizei.com.br/) pela inspiração e conteúdo
