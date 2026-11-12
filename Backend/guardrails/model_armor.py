"""
Cliente de Model Armor (GCP): revisa el prompt del usuario y la respuesta del modelo.

Autenticación por ADC (`gcloud auth application-default login` en local, o la
Service Account adjunta en Cloud Run). No hay claves ni tokens en el .env.

Política ante fallos de Model Armor (red, credenciales, cuota):
    MODEL_ARMOR_FAIL_MODE=closed  → se bloquea el mensaje (por defecto, más seguro)
    MODEL_ARMOR_FAIL_MODE=open    → se deja pasar sin revisar
"""

import os
from dataclasses import dataclass, field

from google.api_core.client_options import ClientOptions
from google.cloud import modelarmor_v1

from dotenv import load_dotenv

load_dotenv()

MODEL_ARMOR_ENABLED = os.getenv("MODEL_ARMOR_ENABLED", "true").strip().lower() == "true"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
MODEL_ARMOR_LOCATION = os.getenv("MODEL_ARMOR_LOCATION", "us-central1")
MODEL_ARMOR_TEMPLATE_ID = os.getenv("MODEL_ARMOR_TEMPLATE_ID")
MODEL_ARMOR_FAIL_MODE = os.getenv("MODEL_ARMOR_FAIL_MODE", "closed").strip().lower()

TIMEOUT_SEGUNDOS = 10
MODOS_FALLO = {"closed", "open"}


@dataclass
class Veredicto:
    """Resultado de una revisión de Model Armor."""

    bloqueado: bool
    filtros: list[str] = field(default_factory=list)  # p. ej. ["pi_and_jailbreak"]
    error: str | None = None  # Model Armor no respondió


def verificar_configuracion() -> None:
    """Falla al arrancar si los guardrails están activos pero mal configurados."""
    if not MODEL_ARMOR_ENABLED:
        return
    faltan = [n for n, v in {"GCP_PROJECT_ID": GCP_PROJECT_ID,
                              "MODEL_ARMOR_TEMPLATE_ID": MODEL_ARMOR_TEMPLATE_ID}.items() if not v]
    if faltan:
        raise RuntimeError(f"Faltan en .env para Model Armor: {', '.join(faltan)}")
    if MODEL_ARMOR_FAIL_MODE not in MODOS_FALLO:
        raise RuntimeError(f"MODEL_ARMOR_FAIL_MODE inválido: {MODEL_ARMOR_FAIL_MODE!r} (closed | open)")


class ModelArmorGuard:
    """Envuelve el cliente regional de Model Armor. Se crea una sola vez."""

    def __init__(self) -> None:
        verificar_configuracion()
        self.template = (
            f"projects/{GCP_PROJECT_ID}/locations/{MODEL_ARMOR_LOCATION}"
            f"/templates/{MODEL_ARMOR_TEMPLATE_ID}"
        )
        self.fail_closed = MODEL_ARMOR_FAIL_MODE == "closed"
        self._client = modelarmor_v1.ModelArmorClient(
            client_options=ClientOptions(
                api_endpoint=f"modelarmor.{MODEL_ARMOR_LOCATION}.rep.googleapis.com"
            )
        )

    def revisar_prompt(self, texto: str) -> Veredicto:
        """Revisa el mensaje del usuario antes de que llegue al modelo."""
        return self._revisar(
            lambda: self._client.sanitize_user_prompt(
                request=modelarmor_v1.SanitizeUserPromptRequest(
                    name=self.template,
                    user_prompt_data=modelarmor_v1.DataItem(text=texto),
                ),
                timeout=TIMEOUT_SEGUNDOS,
            )
        )

    def revisar_respuesta(self, texto: str, prompt: str | None = None) -> Veredicto:
        """Revisa la respuesta del modelo antes de que llegue al cliente."""
        return self._revisar(
            lambda: self._client.sanitize_model_response(
                request=modelarmor_v1.SanitizeModelResponseRequest(
                    name=self.template,
                    model_response_data=modelarmor_v1.DataItem(text=texto),
                    user_prompt=prompt or "",
                ),
                timeout=TIMEOUT_SEGUNDOS,
            )
        )

    def _revisar(self, llamada) -> Veredicto:
        try:
            resultado = llamada().sanitization_result
        except Exception as exc:  # red, credenciales caducadas, cuota, timeout…
            print(f"[model_armor] sin respuesta ({'fail-closed' if self.fail_closed else 'fail-open'}): {exc!r}")
            return Veredicto(bloqueado=self.fail_closed, error=type(exc).__name__)

        bloqueado = resultado.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND
        return Veredicto(bloqueado=bloqueado, filtros=_filtros_detectados(resultado) if bloqueado else [])


def _filtros_detectados(resultado) -> list[str]:
    """Nombres de los filtros que dieron MATCH_FOUND (rai se desglosa por tipo)."""
    detectados = []
    for nombre, filtro in resultado.filter_results.items():
        datos = type(filtro).to_dict(filtro, use_integers_for_enums=False)
        if nombre == "rai":
            tipos = next(iter(datos.values()), {}).get("rai_filter_type_results", {})
            detectados += [f"rai:{t}" for t, v in tipos.items() if v.get("match_state") == "MATCH_FOUND"]
        elif _contiene_match(datos):
            detectados.append(nombre)
    return detectados


def _contiene_match(nodo) -> bool:
    if isinstance(nodo, dict):
        return nodo.get("match_state") == "MATCH_FOUND" or any(_contiene_match(v) for v in nodo.values())
    if isinstance(nodo, list):
        return any(_contiene_match(v) for v in nodo)
    return False
