"""
Middleware de LangChain que aplica Model Armor en las dos direcciones del agente.

    before_agent → revisa el mensaje del usuario. Si se bloquea, el modelo nunca
                   lo ve y el mensaje se BORRA del historial (si quedara, un prompt
                   injection seguiría actuando en los turnos siguientes).
    after_model  → revisa la respuesta del modelo. Si se bloquea, se reemplaza
                   (mismo id) por un texto seguro, también en el historial.

El veredicto del turno queda en state["guardrail"] para que la API lo muestre.
"""

from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.runtime import Runtime
from typing_extensions import NotRequired

from .model_armor import ModelArmorGuard, Veredicto

MENSAJE_PROMPT_BLOQUEADO = (
    "Lo siento, no puedo procesar ese mensaje. Si buscas comprar, alquilar o "
    "vender un inmueble, cuéntame qué necesitas y con gusto te ayudo."
)
MENSAJE_RESPUESTA_BLOQUEADA = (
    "Disculpa, no puedo darte esa respuesta. ¿Te ayudo con otra consulta sobre inmuebles?"
)
MENSAJE_SIN_SERVICIO = (
    "En este momento no puedo verificar tu mensaje de forma segura. "
    "Inténtalo de nuevo en unos minutos."
)


class GuardrailState(AgentState):
    guardrail: NotRequired[dict | None]


def _registro(etapa: str, veredicto: Veredicto) -> dict:
    return {"blocked": True, "stage": etapa, "filters": veredicto.filtros, "error": veredicto.error}


class ModelArmorMiddleware(AgentMiddleware[GuardrailState]):
    state_schema = GuardrailState

    def __init__(self, guard: ModelArmorGuard) -> None:
        super().__init__()
        self.guard = guard  # solo lectura: no se muta entre invocaciones

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: GuardrailState, runtime: Runtime) -> dict[str, Any] | None:
        ultimo = state["messages"][-1]
        if not isinstance(ultimo, HumanMessage):
            return {"guardrail": None}

        veredicto = self.guard.revisar_prompt(ultimo.text)
        if not veredicto.bloqueado:
            return {"guardrail": None}  # limpia el veredicto del turno anterior

        print(f"[guardrail] prompt bloqueado: filtros={veredicto.filtros} error={veredicto.error}")
        return {
            "messages": [
                RemoveMessage(id=ultimo.id),
                AIMessage(MENSAJE_SIN_SERVICIO if veredicto.error else MENSAJE_PROMPT_BLOQUEADO),
            ],
            "guardrail": _registro("input", veredicto),
            "jump_to": "end",
        }

    def after_model(self, state: GuardrailState, runtime: Runtime) -> dict[str, Any] | None:
        respuesta = state["messages"][-1]
        if not isinstance(respuesta, AIMessage) or respuesta.tool_calls or not respuesta.text:
            return None  # llamadas a tools (cuando existan) no se revisan aquí

        prompt = next((m.text for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
        veredicto = self.guard.revisar_respuesta(respuesta.text, prompt)
        if not veredicto.bloqueado:
            return None

        print(f"[guardrail] respuesta bloqueada: filtros={veredicto.filtros} error={veredicto.error}")
        texto = MENSAJE_SIN_SERVICIO if veredicto.error else MENSAJE_RESPUESTA_BLOQUEADA
        return {
            "messages": [AIMessage(id=respuesta.id, content=texto)],  # mismo id → reemplaza
            "guardrail": _registro("output", veredicto),
        }
