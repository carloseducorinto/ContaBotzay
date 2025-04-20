from typing import List, Dict, Any
from langgraph.graph import StateGraph, END, Graph
from pydantic import BaseModel
import logging
from agents.welcome_agent import WelcomeAgent
from agents.company_opening_agent import CompanyOpeningAgent

# Configure logging
logger = logging.getLogger(__name__)

class AgentState(BaseModel):
    message: str
    chat_history: List[Dict[str, str]]
    response: str | None = None
    next_agent: str = "welcome_agent"          # welcome_agent | company_opening_agent | end_node


class AgentManager:
    """Coordena os nós/agents e guarda a última 'next_agent' para a UI."""

    def __init__(self, llm_provider: str = "openai"):
        logger.info("Initializing AgentManager")
        self.llm_provider = llm_provider
        self.workflow: Graph = self._create_workflow()
        self.last_next_agent: str = "end_node"      # flag lida pela interface
        self.agents = {
            "welcome_agent": WelcomeAgent(self.llm_provider),
            "company_opening_agent": CompanyOpeningAgent(self.llm_provider),
        }
        logger.debug("All agents initialized successfully")

    # ------------------------ routing helper ---------------------------------
    @staticmethod
    def _route(state: "AgentState") -> str:
        logger.debug(f"Routing to next agent: {state.next_agent}")
        return state.next_agent or "end_node"

    # --------------------------- graph ---------------------------------------
    def _create_workflow(self) -> Graph:
        logger.debug("Creating workflow graph")
        workflow = StateGraph(AgentState)

        workflow.add_node("welcome_agent",          self._welcome_agent)
        workflow.add_node("company_opening_agent",  self._company_opening_agent)
        workflow.add_node("end_node",               self._end_workflow)

        workflow.add_conditional_edges(
            "welcome_agent",
            self._route,
            {
                "company_opening_agent": "company_opening_agent",
                "end_node":             "end_node",
            },
        )

        workflow.add_edge("company_opening_agent", "end_node")
        workflow.add_edge("end_node", END)
        workflow.set_entry_point("welcome_agent")
        logger.debug("Workflow graph created successfully")
        return workflow.compile()

    # ---------------------------- nodes --------------------------------------
    def _welcome_agent(self, state: "AgentState") -> Dict[str, Any]:
        logger.debug("Executing welcome agent")
        return self.agents["welcome_agent"].process(state.model_dump())

    def _company_opening_agent(self, state: "AgentState") -> Dict[str, Any]:
        logger.debug("Executing company opening agent")
        return self.agents["company_opening_agent"].process(state.model_dump())

    @staticmethod
    def _end_workflow(state: "AgentState") -> Dict[str, Any]:
        logger.debug("Ending workflow")
        return {}

    # -------------------------- public API -----------------------------------
    def process_message(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
    ) -> str:
        """Executa o workflow e devolve apenas o texto de resposta.
        Atributo self.last_next_agent indica a próxima etapa do grafo."""
        try:
            logger.info(f"Processing message: {message[:50]}...")
            initial_state = AgentState(
                message=message, chat_history=chat_history, next_agent="welcome_agent"
            )
            result = self.workflow.invoke(initial_state)             # AddableValuesDict
            self.last_next_agent = result.get("next_agent", "end_node")
            logger.info(f"Message processed, next agent: {self.last_next_agent}")
            return result.get("response", "No response produced.")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return "Desculpe, ocorreu um erro no processamento."

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Processa a mensagem do usuário através do fluxo de agentes."""
        try:
            logger.info(f"Processing message with current agent: {state.get('current_agent', 'welcome_agent')}")
            
            if "current_agent" not in state:
                logger.warning("No current agent specified, defaulting to welcome_agent")
                state["current_agent"] = "welcome_agent"

            agent = self.agents.get(state["current_agent"])
            if not agent:
                logger.error(f"Agent not found: {state['current_agent']}")
                return {
                    "response": "Desculpe, ocorreu um erro no processamento.",
                    "current_agent": "end_node",
                }

            result = agent.process(state)
            logger.info(f"Agent {state['current_agent']} processed message, next agent: {result.get('next_agent')}")
            
            return {
                "response": result["response"],
                "current_agent": result["next_agent"],
            }
        except Exception as e:
            logger.error(f"Error in agent manager process: {str(e)}", exc_info=True)
            return {
                "response": "Desculpe, ocorreu um erro no processamento.",
                "current_agent": "end_node",
            }
