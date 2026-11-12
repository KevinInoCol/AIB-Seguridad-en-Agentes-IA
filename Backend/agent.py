"""
Orquestador del agente inmobiliario: ensambla modelo, prompt, memoria y guardrails.

Sin tools por ahora. Los recursos se crean una sola vez (init_resources) y
cada conversación se distingue por su thread_id.
"""

import os
from datetime import date
from pathlib import Path

import yaml
from langchain.agents import create_agent

from dotenv import load_dotenv

from chat_history import build_checkpointer
from guardrails import build_guardrails
from model_config import build_llm

load_dotenv()

BOT_NAME = os.getenv("BOT_NAME", "Valeria")
EMPRESA = os.getenv("EMPRESA", "Inmobiliaria Andina")

RUTA_PROMPT = Path(__file__).parent / "prompt" / "system_prompt.yaml"

_agent = None


def _render_system_prompt() -> str:
    """Lee el YAML del prompt e inyecta los placeholders."""
    with open(RUTA_PROMPT, encoding="utf-8") as f:
        prompt = yaml.safe_load(f)["system_prompt"]
    return (
        prompt.replace("{bot_name}", BOT_NAME)
        .replace("{empresa}", EMPRESA)
        .replace("{fecha_actual}", date.today().isoformat())
    )


def init_resources() -> None:
    """Crea el agente una sola vez al arrancar el proceso."""
    global _agent
    _agent = create_agent(
        model=build_llm(),
        tools=[],
        system_prompt=_render_system_prompt(),
        checkpointer=build_checkpointer(),
        middleware=build_guardrails(),
    )


def responder(mensaje: str, thread_id: str) -> tuple[str, dict | None]:
    """Envía un mensaje al agente dentro de la conversación `thread_id`.

    Devuelve (respuesta, guardrail): guardrail es None si nada se bloqueó, o
    {"blocked", "stage": "input"|"output", "filters", "error"} si se bloqueó.
    """
    if _agent is None:
        init_resources()
    resultado = _agent.invoke(
        {"messages": [{"role": "user", "content": mensaje}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return resultado["messages"][-1].text, resultado.get("guardrail")
