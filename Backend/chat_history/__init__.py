"""
Histórico de conversación VOLÁTIL: vive en la RAM del proceso.

InMemorySaver guarda el estado por thread_id (uno por conversación). Al
reiniciar el proceso se pierde todo. Para persistirlo, se reemplaza este
checkpointer por PostgresSaver sin tocar agent.py.
"""

from langgraph.checkpoint.memory import InMemorySaver


def build_checkpointer() -> InMemorySaver:
    """Checkpointer en memoria compartido por todas las conversaciones."""
    return InMemorySaver()
