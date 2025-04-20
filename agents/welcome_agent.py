# agents/welcome_agent.py  – versão completa, com logging e modelos atualizados

from __future__ import annotations
from typing import Dict, Any
import json
import os
import logging

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from utils.webscraper import ContabilizeiScraper

# --------------------------------------------------------------------------- #
#                                LOGGING                                      #
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
load_dotenv()


# --------------------------------------------------------------------------- #
#                SCHEMA JSON QUE A LLM DEVE DEVOLVER                          #
# --------------------------------------------------------------------------- #
class IntentOutput(BaseModel):
    response: str = Field(..., description="Texto final para o usuário")
    intent: str = Field(..., description="abrir_empresa ou geral")


INTENT_TO_AGENT = {
    "abrir_empresa": "company_opening_agent",
    "geral": "end_node",
}


# --------------------------------------------------------------------------- #
#                                 AGENTE                                      #
# --------------------------------------------------------------------------- #
class WelcomeAgent:
    """Primeiro contato – detecta dinamicamente a intenção do usuário."""

    def __init__(self, llm_provider: str = "openai"):
        logger.info(f"Initializing WelcomeAgent with {llm_provider} provider")
        self.llm = self._init_llm(llm_provider)
        self.scraper = ContabilizeiScraper()
        self.prompt = self._create_prompt()
        logger.debug("WelcomeAgent initialization completed")

    # --------------------------------------------------------------------- #
    #                           LLM LOADER                                  #
    # --------------------------------------------------------------------- #
    @staticmethod
    def _init_llm(provider: str):
        try:
            provider = provider.lower()
            if provider == "openai":
                logger.debug("Initializing OpenAI LLM (gpt‑4o-mini)")
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=os.getenv("OPENAI_API_KEY"),
                )
            if provider == "groq":
                logger.debug("Initializing Groq LLM (llama3-70b-8192)")
                return ChatGroq(
                    model="llama3-70b-8192",          # modelo em produção no Groq
                    temperature=0,
                    api_key=os.getenv("GROQ_API_KEY"),
                )
            raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Error initializing LLM", exc_info=True)
            raise

    # --------------------------------------------------------------------- #
    #                              PROMPT                                   #
    # --------------------------------------------------------------------- #
    @staticmethod
    def _create_prompt() -> ChatPromptTemplate:
        logger.debug("Creating welcome prompt template")
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Você é um assistente da Contabilizei.\n"
                    "Classifique a intenção do usuário:\n"
                    " • abrir empresa/CNPJ  -> intent = abrir_empresa\n"
                    " • outro assunto       -> intent = geral\n\n"
                    "Responda em JSON puro compatível com:\n"
                    '{{"response": <texto>, "intent": <string>}}'
                ),
                ("system", "Trechos do site:\n{website_content}"),
                ("human", "{message}"),
            ]
        )

    # --------------------------------------------------------------------- #
    #                     PARSE & SAFEGUARD LLM OUTPUT                      #
    # --------------------------------------------------------------------- #
    @staticmethod
    def _json_safe(chain, vars: dict) -> IntentOutput:
        raw = chain.invoke(vars)
        logger.debug(f"Raw LLM output: {raw[:120]}...")
        try:
            return IntentOutput(**json.loads(raw))
        except Exception:
            logger.error("Failed to parse LLM JSON", exc_info=True)
            return IntentOutput(
                response="Desculpe, não entendi sua solicitação.",
                intent="geral",
            )

    # --------------------------------------------------------------------- #
    #                               MAIN                                    #
    # --------------------------------------------------------------------- #
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing welcome message: {state.get('message', '')[:60]}...")

        # 1) Usa ferramenta de web‑scraper
        try:
            logger.debug("Fetching website content")
            site_excerpt = self.scraper.search_content(state["message"])
            logger.debug(f"Website excerpt retrieved: {site_excerpt[:120]}...")
        except Exception:
            logger.error("Error fetching website content", exc_info=True)
            site_excerpt = "Conteúdo indisponível."

        # 2) Chama LLM
        chain = self.prompt | self.llm | StrOutputParser()
        result = self._json_safe(
            chain,
            {"website_content": site_excerpt, "message": state["message"]},
        )

        next_agent = INTENT_TO_AGENT.get(result.intent, "end_node")
        logger.info(f"Intent detected: {result.intent} → next agent: {next_agent}")

        return {
            "response": result.response,
            "next_agent": next_agent,
        }
