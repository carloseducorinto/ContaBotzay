# agents/company_opening_agent.py  – atualizado: mantém next_agent para tela de upload
from typing import Dict, Any
import os
import logging

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

# --------------------------------------------------------------------------- #
#                                LOGGING                                      #
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
load_dotenv()

# --------------------------------------------------------------------------- #
#                             LISTA DE DOCUMENTOS                             #
# --------------------------------------------------------------------------- #
DOCS_LIST = (
    "- RG e CPF do(s) proprietário(s)\n"
    "- Comprovante de endereço atualizado\n"
    "- Certidão de casamento (se aplicável)\n"
    "- Cópia do IPTU ou documento com inscrição imobiliária\n"
    "- Registro em conselho profissional (se exigido pela atividade)"
)


class CompanyOpeningAgent:
    """Especialista em abertura gratuita de empresa/CNPJ pela Contabilizei."""

    # --------------------------------------------------------------------- #
    #                                INIT                                   #
    # --------------------------------------------------------------------- #
    def __init__(self, llm_provider: str = "openai"):
        self.llm_provider = llm_provider.lower()
        logger.info(f"Initializing CompanyOpeningAgent with {self.llm_provider} provider")
        self.llm = self._initialize_llm()
        self.prompt = self._create_prompt()

    # --------------------------------------------------------------------- #
    #                           LLM INITIALIZER                             #
    # --------------------------------------------------------------------- #
    def _initialize_llm(self):
        try:
            if self.llm_provider == "openai":
                logger.debug("Loading OpenAI model: gpt‑4o‑mini")
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=os.getenv("OPENAI_API_KEY"),
                )
            if self.llm_provider == "groq":
                logger.debug("Loading Groq model: llama3-70b-8192")
                return ChatGroq(
                    model="llama3-70b-8192",
                    temperature=0,
                    api_key=os.getenv("GROQ_API_KEY"),
                )
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        except Exception:
            logger.error("Error initializing LLM", exc_info=True)
            raise

    # --------------------------------------------------------------------- #
    #                              PROMPT                                   #
    # --------------------------------------------------------------------- #
    @staticmethod
    def _create_prompt() -> ChatPromptTemplate:
        logger.debug("Creating company opening prompt template")
        return ChatPromptTemplate.from_messages(
            [
                (
                "system",
                "Você é um consultor especializado em abertura de empresas na Contabilizei. "
                "Em tom profissional e objetivo, apresente de forma sucinta as etapas do processo, "
                "detalhe as taxas governamentais obrigatórias e liste os documentos necessários:\n"
                f"{DOCS_LIST}"
                                                
                ),
                
                ("human", "{message}"),
            ]
        )

    # --------------------------------------------------------------------- #
    #                              PROCESS                                  #
    # --------------------------------------------------------------------- #
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Processing company opening message: {state.get('message', '')[:60]}...")
            if "message" not in state:
                logger.warning("No message found in state")
                return {
                    "response": "Desculpe, não entendi sua mensagem.",
                    "next_agent": "company_opening_agent",  # mantém tela de upload
                }

            chain = self.prompt | self.llm | StrOutputParser()
            response = chain.invoke({"message": state["message"]})
            logger.debug(f"LLM response: {response[:120]}...")

            # ❗ Mantém next_agent para que a UI continue exibindo uploads
            return {
                "response": response,
                "next_agent": "company_opening_agent",
            }
        except Exception:
            logger.error("Error in CompanyOpeningAgent", exc_info=True)
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua solicitação.",
                "next_agent": "company_opening_agent",
            }
