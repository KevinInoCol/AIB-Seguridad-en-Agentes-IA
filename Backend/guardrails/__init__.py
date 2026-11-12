"""
Capa de guardrails del agente (Model Armor de GCP).

Se activa o desactiva con MODEL_ARMOR_ENABLED en el .env.
"""

from .middleware import ModelArmorMiddleware
from .model_armor import (
    MODEL_ARMOR_ENABLED,
    MODEL_ARMOR_FAIL_MODE,
    MODEL_ARMOR_TEMPLATE_ID,
    ModelArmorGuard,
)


def build_guardrails() -> list:
    """Middleware de guardrails para create_agent (lista vacía si está desactivado)."""
    if not MODEL_ARMOR_ENABLED:
        return []
    return [ModelArmorMiddleware(ModelArmorGuard())]


def guardrails_info() -> dict:
    """Estado de la capa de guardrails, para /api/health."""
    return {
        "enabled": MODEL_ARMOR_ENABLED,
        "provider": "model-armor" if MODEL_ARMOR_ENABLED else None,
        "template": MODEL_ARMOR_TEMPLATE_ID if MODEL_ARMOR_ENABLED else None,
        "fail_mode": MODEL_ARMOR_FAIL_MODE if MODEL_ARMOR_ENABLED else None,
    }
