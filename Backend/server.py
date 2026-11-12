"""
API HTTP del agente inmobiliario para el frontend de React.

Capa de I/O: solo conoce la API pública de agent.py. El frontend genera un
thread_id por conversación; el historial vive en la RAM de este proceso, así
que reiniciar el servidor borra todas las conversaciones.

Ejecutar (desde Backend/):
    .venv/bin/uvicorn server:app --reload --port 8000
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from agent import BOT_NAME, EMPRESA, init_resources, responder
from model_config import load_model_config

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(min_length=1, max_length=100)


class ChatResponse(BaseModel):
    reply: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Valida la config y crea el agente una sola vez al arrancar."""
    cfg = load_model_config()
    if cfg["provider"] == "openai" and not OPENAI_API_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en Backend/.env (ver .env.example).")
    init_resources()
    yield


app = FastAPI(title="Agente Inmobiliario", lifespan=lifespan)


@app.get("/api/health")
def health() -> dict:
    """Estado del backend y modelo activo (lo muestra la cabecera del chat)."""
    cfg = load_model_config()
    return {
        "status": "ok",
        "provider": cfg["provider"],
        "model": cfg["model"],
        "bot_name": BOT_NAME,
        "empresa": EMPRESA,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Envía un mensaje al agente dentro de la conversación `thread_id`."""
    try:
        reply = await run_in_threadpool(responder, req.message, req.thread_id)
    except Exception as exc:  # el detalle va al log del servidor, no al cliente
        print(f"[chat] error en thread {req.thread_id}: {exc!r}")
        raise HTTPException(status_code=502, detail="El modelo no respondió. Revisa el backend.")
    return ChatResponse(reply=reply)
