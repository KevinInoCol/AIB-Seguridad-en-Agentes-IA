"""
Entrypoint de consola para conversar con el agente inmobiliario.

Toda la sesión usa un mismo thread_id, así que el agente recuerda lo dicho
mientras el proceso siga vivo. Al salir, el historial se pierde (RAM).

Ejecutar:
    python app.py
"""

import os
import uuid

from dotenv import load_dotenv

from agent import init_resources, responder
from model_config import load_model_config

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COMANDOS_SALIDA = {"salir", "exit", "quit"}


def verificar_configuracion() -> dict:
    """Falla antes de llamar al modelo si la config del proveedor está incompleta."""
    cfg = load_model_config()
    if cfg["provider"] == "openai" and not OPENAI_API_KEY:
        raise SystemExit("Falta OPENAI_API_KEY en el .env (ver .env.example).")
    return cfg


if __name__ == "__main__":
    cfg = verificar_configuracion()
    init_resources()
    thread_id = str(uuid.uuid4())
    print(f"Agente inmobiliario listo ({cfg['provider']}: {cfg['model']}). "
          "Escribe 'salir' para terminar.\n")
    while True:
        mensaje = input("Tú: ").strip()
        if not mensaje:
            continue
        if mensaje.lower() in COMANDOS_SALIDA:
            break
        respuesta, guardrail = responder(mensaje, thread_id)
        if guardrail:
            print(f"[guardrail] bloqueado en {guardrail['stage']}: {guardrail['filters'] or guardrail['error']}")
        print(f"Agente: {respuesta}\n")
