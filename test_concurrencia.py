"""Prueba opcional en vivo: crea 5 tareas de pago y aprueba cada una al llegar a HITL.

Requiere API, OpenAI, Pinecone y LangSmith operativos. No ejecutar como pytest.
"""
import asyncio
import math
import time
import httpx

BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT_SECONDS = 180
CLIENTES = [102, 205, 102, 205, 102]


def percentile_95(values):
    ordered = sorted(values)
    position = (len(ordered) - 1) * .95
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


async def run_task(client, number, cliente_id):
    prompt = (f'Buscá los pedidos del cliente {cliente_id} y calculá cantidad, total y promedio. '
              'Usá las herramientas comerciales y validá el resultado.')
    began = time.perf_counter()
    resp = await client.post(f'{BASE_URL}/tasks', json={'prompt': prompt})
    resp.raise_for_status()
    post_time = time.perf_counter() - began
    job_id = resp.json()['job_id']
    approved = False
    while time.perf_counter() - began < TIMEOUT_SECONDS:
        await asyncio.sleep(1)
        response = await client.get(f'{BASE_URL}/tasks/{job_id}')
        response.raise_for_status()
        status = response.json()['status']
        if status == 'WAITING_APPROVAL' and not approved:
            approval = await client.post(f'{BASE_URL}/tasks/{job_id}/approve', json={'approved': True})
            approval.raise_for_status()
            approved = True
        if status in {'COMPLETED', 'FAILED', 'REJECTED'}:
            return {'number': number, 'job_id': job_id, 'status': status,
                    'post': post_time, 'total': time.perf_counter() - began}
    return {'number': number, 'job_id': job_id, 'status': 'TIMEOUT',
            'post': post_time, 'total': time.perf_counter() - began}


async def main():
    async with httpx.AsyncClient(timeout=45) as client:
        began = time.perf_counter()
        results = await asyncio.gather(*(
            run_task(client, i, cid) for i, cid in enumerate(CLIENTES, 1)))
        global_time = time.perf_counter() - began
    for result in results:
        print(result)
    print('Total:', round(global_time, 2), 's')
    print('P95 POST:', round(percentile_95([r['post'] for r in results]), 3), 's')
    print('P95 tarea:', round(percentile_95([r['total'] for r in results]), 2), 's')
    assert all(r['status'] == 'COMPLETED' for r in results), 'Algunas tareas no completaron'


if __name__ == '__main__':
    asyncio.run(main())
