"""
Carga model_config/model.yaml y construye el ChatOpenAI del agente.

El YAML es la fuente de verdad; OPENAI_MODEL en el .env solo sobrescribe el
nombre del modelo (útil para probar otro sin tocar el archivo).
"""

import os
from pathlib import Path

import yaml
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL")

RUTA_MODEL_YAML = Path(__file__).with_name("model.yaml")
NIVELES_RAZONAMIENTO = {"minimal", "low", "medium", "high"}


def load_model_config() -> dict:
    """Devuelve la sección `llm` del YAML con los overrides de entorno aplicados."""
    with open(RUTA_MODEL_YAML, encoding="utf-8") as f:
        llm_cfg = yaml.safe_load(f)["llm"]

    if OPENAI_MODEL:
        llm_cfg["model"] = OPENAI_MODEL

    if llm_cfg["reasoning_effort"] not in NIVELES_RAZONAMIENTO:
        raise ValueError(
            f"reasoning_effort inválido: {llm_cfg['reasoning_effort']!r}. "
            f"Usa uno de {sorted(NIVELES_RAZONAMIENTO)}."
        )
    return llm_cfg


def build_llm() -> ChatOpenAI:
    """Instancia el modelo de OpenAI según model.yaml."""
    cfg = load_model_config()
    return ChatOpenAI(model=cfg["model"], reasoning_effort=cfg["reasoning_effort"])
