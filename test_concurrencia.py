import asyncio
import math
import time

import httpx


BASE_URL = "http://127.0.0.1:8000"

PROMPTS = [
    (
        f"Consulta los pedidos del cliente con ID {cliente_id} usando "
        "buscar_pedidos. Luego utiliza el agente analyst y la herramienta "
        "analizar_pedidos para calcular la cantidad, el total y el promedio. "
        "Finalmente, valida los resultados."
    )
    for cliente_id in [102, 205, 102, 205, 102]
]


def percentil_95(valores):
    ordenados = sorted(valores)
    posicion = (len(ordenados) - 1) * 0.95

    inferior = math.floor(posicion)
    superior = math.ceil(posicion)

    if inferior == superior:
        return ordenados[inferior]

    fraccion = posicion - inferior
    return (
        ordenados[inferior] * (1 - fraccion)
        + ordenados[superior] * fraccion
    )


async def ejecutar_tarea(cliente, numero, prompt):
    inicio = time.perf_counter()

    respuesta = await cliente.post(
        f"{BASE_URL}/tasks",
        json={"prompt": prompt},
    )
    respuesta.raise_for_status()

    tiempo_post = time.perf_counter() - inicio
    job_id = respuesta.json()["job_id"]

    while True:
        await asyncio.sleep(1)

        consulta = await cliente.get(
            f"{BASE_URL}/tasks/{job_id}"
        )
        consulta.raise_for_status()

        datos = consulta.json()
        estado = datos["status"]

        if estado in ("COMPLETED", "FAILED"):
            duracion_total = time.perf_counter() - inicio

            return {
                "numero": numero,
                "job_id": job_id,
                "status": estado,
                "post_seconds": tiempo_post,
                "total_seconds": duracion_total,
            }


async def main():
    async with httpx.AsyncClient(timeout=30.0) as cliente:
        inicio_global = time.perf_counter()

        resultados = await asyncio.gather(
            *[
                ejecutar_tarea(cliente, i, prompt)
                for i, prompt in enumerate(PROMPTS, start=1)
            ]
        )

        duracion_global = time.perf_counter() - inicio_global

    print("\nRESULTADOS DE CONCURRENCIA")
    print("-" * 65)

    for resultado in resultados:
        print(
            f"Tarea {resultado['numero']} | "
            f"{resultado['status']} | "
            f"POST: {resultado['post_seconds']:.3f}s | "
            f"Total: {resultado['total_seconds']:.2f}s"
        )

    print("\nMÉTRICAS")
    print(f"Solicitudes: {len(resultados)}")
    print(f"Duración global: {duracion_global:.2f}s")

    print(
        "P95 respuesta POST: "
        f"{percentil_95([r['post_seconds'] for r in resultados]):.3f}s"
    )

    print(
        "P95 ejecución completa: "
        f"{percentil_95([r['total_seconds'] for r in resultados]):.2f}s"
    )

    completadas = sum(
        r["status"] == "COMPLETED" for r in resultados
    )
    print(f"Tareas completadas: {completadas}/5")


if __name__ == "__main__":
    asyncio.run(main())