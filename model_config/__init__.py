"""
Carga model_config/model.yaml y construye el chat model del proveedor activo.

El proveedor se conmuta con LLM_PROVIDER en el .env (openai | ollama). El YAML
guarda los parámetros de cada uno; las variables OPENAI_MODEL, OLLAMA_MODEL y
OLLAMA_BASE_URL solo sobrescriben valores puntuales para pruebas.
"""

import os
from pathlib import Path

import yaml
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

RUTA_MODEL_YAML = Path(__file__).with_name("model.yaml")
PROVEEDORES = {"openai", "ollama"}
NIVELES_RAZONAMIENTO = {"none", "minimal", "low", "medium", "high"}


def load_model_config() -> dict:
    """Devuelve {'provider': ..., **params} del proveedor activo, con overrides."""
    with open(RUTA_MODEL_YAML, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    provider = (LLM_PROVIDER or cfg["default_provider"]).strip().lower()
    if provider not in PROVEEDORES:
        raise ValueError(
            f"LLM_PROVIDER inválido: {provider!r}. Usa uno de {sorted(PROVEEDORES)}."
        )

    params = dict(cfg["providers"][provider])
    if provider == "openai":
        if OPENAI_MODEL:
            params["model"] = OPENAI_MODEL
        if params["reasoning_effort"] not in NIVELES_RAZONAMIENTO:
            raise ValueError(
                f"reasoning_effort inválido: {params['reasoning_effort']!r}. "
                f"Usa uno de {sorted(NIVELES_RAZONAMIENTO)}."
            )
    else:
        if OLLAMA_MODEL:
            params["model"] = OLLAMA_MODEL
        if OLLAMA_BASE_URL:
            params["base_url"] = OLLAMA_BASE_URL

    return {"provider": provider, **params}


def build_llm() -> BaseChatModel:
    """Instancia el chat model del proveedor activo según model.yaml."""
    cfg = load_model_config()
    if cfg["provider"] == "openai":
        return ChatOpenAI(model=cfg["model"], reasoning_effort=cfg["reasoning_effort"])
    return ChatOllama(
        model=cfg["model"],
        base_url=cfg["base_url"],
        temperature=cfg["temperature"],
        reasoning=cfg["reasoning"],
        validate_model_on_init=True,  # falla al arrancar si no hiciste `ollama pull`
    )
