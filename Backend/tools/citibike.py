"""
Tool que consulta en BigQuery las estaciones de Citi Bike (Nueva York).

Usa el dataset público `bigquery-public-data.new_york_citibike`. La consulta se
factura al proyecto GCP_PROJECT_ID (mínimo 10 MB por consulta, dentro del 1 TB
gratis al mes). Autenticación por ADC, igual que Model Armor.

Seguridad: el LLM NUNCA escribe SQL. Solo aporta un texto de búsqueda que entra
como parámetro (@texto), así que no hay SQL injection posible. Además hay un
tope de bytes facturados y de filas devueltas.

Probar sin el LLM:
    python -m tools.citibike Broadway
"""

import os
import sys

from google.cloud import bigquery
from langchain.tools import tool

from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

TABLA_ESTACIONES = "bigquery-public-data.new_york_citibike.citibike_stations"
MAX_BYTES_FACTURADOS = 50 * 1024 * 1024  # 50 MB; BigQuery cobra mínimo 10 MB
MAX_RESULTADOS = 10
LARGO_MAX_TEXTO = 60

CONSULTA = f"""
SELECT name, capacity, num_bikes_available, num_docks_available,
       is_renting, is_returning, latitude, longitude, last_reported
FROM `{TABLA_ESTACIONES}`
WHERE is_installed AND LOWER(name) LIKE CONCAT('%', LOWER(@texto), '%')
ORDER BY num_bikes_available DESC
LIMIT @limite
"""

_cliente: bigquery.Client | None = None


def _get_cliente() -> bigquery.Client:
    """Cliente de BigQuery creado una sola vez (perezoso)."""
    global _cliente
    if _cliente is None:
        _cliente = bigquery.Client(project=GCP_PROJECT_ID)
    return _cliente


def buscar_estaciones_citibike(texto: str, limite: int = 5) -> list[dict]:
    """Estaciones instaladas cuyo nombre contiene `texto`. Lanza si BigQuery falla."""
    texto = texto.strip()[:LARGO_MAX_TEXTO]
    limite = max(1, min(int(limite), MAX_RESULTADOS))
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("texto", "STRING", texto),
            bigquery.ScalarQueryParameter("limite", "INT64", limite),
        ],
        maximum_bytes_billed=MAX_BYTES_FACTURADOS,
    )
    filas = _get_cliente().query(CONSULTA, job_config=config).result(timeout=30)
    return [dict(f) for f in filas]


def _formatear(estaciones: list[dict], texto: str) -> str:
    if not estaciones:
        return f"No hay estaciones de Citi Bike cuyo nombre contenga '{texto}'."
    lineas = [f"Estaciones de Citi Bike que coinciden con '{texto}':"]
    for e in estaciones:
        estado = "operativa" if e["is_renting"] else "sin alquiler en este momento"
        lineas.append(
            f"- {e['name']}: {e['num_bikes_available']} bicis disponibles, "
            f"{e['num_docks_available']} anclajes libres (capacidad {e['capacity']}), "
            f"{estado}. Actualizado {e['last_reported']:%Y-%m-%d %H:%M} UTC."
        )
    return "\n".join(lineas)


@tool
def consultar_citibike(calle: str, limite: int = 5) -> str:
    """Consulta en tiempo real las estaciones de bicicletas Citi Bike de NUEVA YORK
    (bicis disponibles, anclajes libres y capacidad) cerca de una calle o avenida.

    Úsala cuando el cliente pregunte por movilidad en bicicleta, estaciones de
    Citi Bike o transporte cerca de una dirección de Nueva York (Manhattan,
    Brooklyn, Queens, Jersey City). NO la uses para inmuebles, precios ni
    direcciones fuera de Nueva York: no tiene esos datos.

    Args:
        calle: nombre de calle, avenida o intersección TAL COMO se escribe en
            inglés, una sola palabra clave es mejor. Ej: 'Broadway', 'W 42 St',
            'Atlantic Ave', 'Bedford'.
        limite: cuántas estaciones devolver (1 a 10). Por defecto 5.
    """
    try:
        return _formatear(buscar_estaciones_citibike(calle, limite), calle)
    except Exception as exc:  # al LLM le llega un texto usable, nunca la excepción
        print(f"[citibike] error consultando BigQuery: {exc!r}")
        return "No pude consultar las estaciones de Citi Bike ahora. Ofrece intentarlo más tarde."


if __name__ == "__main__":
    busqueda = sys.argv[1] if len(sys.argv) > 1 else "Broadway"
    print(consultar_citibike.invoke({"calle": busqueda}))
