# ui/streamlit_app.py  –  coloca set_page_config uma única vez e logo após importar Streamlit
import os
import logging
from typing import List, Dict, cast

import streamlit as st

# ➜ TEM que vir antes de QUALQUER outro comando st.*
st.set_page_config(page_title="Contabilizei Chatbot", page_icon="💬", layout="wide")

from dotenv import load_dotenv
from manager.agent_manager import AgentManager

# ----------------------------------------------------------------------------
#                            LOGGING & ENVIRONMENT
# ----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


# ----------------------------------------------------------------------------
#                        SESSION‑STATE INITIALIZATION
# ----------------------------------------------------------------------------
def init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = cast(List[Dict[str, str]], [])
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "openai"
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = AgentManager(st.session_state.llm_provider)
    if "show_upload" not in st.session_state:
        st.session_state.show_upload = False


# ----------------------------------------------------------------------------
#                               SIDEBAR
# ----------------------------------------------------------------------------
def sidebar() -> None:
    with st.sidebar:
        st.title("⚙️ Configurações")

        prov = st.radio(
            "Provedor LLM:", ["OpenAI", "Groq"],
            index=0 if st.session_state.llm_provider == "openai" else 1,
        )
        if prov.lower() != st.session_state.llm_provider:
            logger.info(f"Alterando provedor para {prov.lower()}")
            st.session_state.llm_provider = prov.lower()
            st.session_state.agent_manager = AgentManager(st.session_state.llm_provider)

        api_key = st.text_input(
            f"{prov} API Key", type="password",
            value=os.getenv(f"{prov.upper()}_API_KEY", ""),
        )
        if api_key:
            os.environ[f"{prov.upper()}_API_KEY"] = api_key

        if st.button("🗑️ Limpar conversa"):
            st.session_state.messages.clear()
            st.session_state.show_upload = False
            st.session_state.agent_manager.last_next_agent = "end_node"


# ----------------------------------------------------------------------------
#                                 MAIN CHAT UI
# ----------------------------------------------------------------------------
def chat_ui() -> None:
    mgr: AgentManager = st.session_state.agent_manager

    st.title("💬 Contabilizei Chatbot")
    st.markdown("Bem‑vindo ao assistente virtual da Contabilizei!")

    # histórico
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # input
    if prompt := st.chat_input("Digite sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    reply = mgr.process_message(prompt, st.session_state.messages)
                except Exception:
                    logger.exception("Erro no processamento do agente")
                    reply = "Desculpe, ocorreu um erro. Tente novamente."
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # se intenção = abrir empresa, ativa uploads
        if mgr.last_next_agent == "company_opening_agent":
            st.session_state.show_upload = True

    # seção de upload
    if st.session_state.show_upload:
        st.markdown("### 📑 Faça upload dos documentos para abrir seu CNPJ")
        st.session_state.docs_uploads = {
            "rg_cpf": st.file_uploader("RG e CPF do(s) proprietário(s)", type=["pdf", "jpg", "png"]),
            "comprov_end": st.file_uploader("Comprovante de endereço atualizado", type=["pdf", "jpg", "png"]),
            "cert_cas": st.file_uploader("Certidão de casamento (se aplicável)", type=["pdf", "jpg", "png"]),
            "iptu": st.file_uploader("Cópia do IPTU/inscrição imobiliária", type=["pdf", "jpg", "png"]),
            "conselho": st.file_uploader(
                "Registro em conselho profissional (se exigido pela atividade)", type=["pdf", "jpg", "png"]),
        }


# ----------------------------------------------------------------------------
#                             PAGE ENTRY POINT
# ----------------------------------------------------------------------------
def main() -> None:
    init_session()
    sidebar()
    chat_ui()


# Quando executado via `streamlit run ui/streamlit_app.py`
# ou importado e chamado por outra module
if __name__ == "__main__":
    main()
