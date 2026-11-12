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

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COMANDOS_SALIDA = {"salir", "exit", "quit"}


def verificar_configuracion() -> None:
    """Falla antes de llamar al modelo si falta la API key."""
    if not OPENAI_API_KEY:
        raise SystemExit("Falta OPENAI_API_KEY en el .env (ver .env.example).")


if __name__ == "__main__":
    verificar_configuracion()
    init_resources()
    thread_id = str(uuid.uuid4())
    print("Agente inmobiliario listo. Escribe 'salir' para terminar.\n")
    while True:
        mensaje = input("Tú: ").strip()
        if not mensaje:
            continue
        if mensaje.lower() in COMANDOS_SALIDA:
            break
        print(f"Agente: {responder(mensaje, thread_id)}\n")
