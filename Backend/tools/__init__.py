"""
Tools del agente. Un archivo por tool: función imperativa (testeable sin LLM)
+ la tool de LangChain que ve el modelo.
"""

from .citibike import buscar_estaciones_citibike, consultar_citibike


def build_tools() -> list:
    """Tools compartidas por todas las conversaciones (se crean una vez)."""
    return [consultar_citibike]


__all__ = ["build_tools", "buscar_estaciones_citibike", "consultar_citibike"]
