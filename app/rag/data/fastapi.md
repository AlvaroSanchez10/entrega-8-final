# FastAPI

FastAPI es un framework moderno para construir APIs web en Python. Fue diseñado para aprovechar type hints de Python y ofrecer una experiencia de desarrollo rápida, validación automática de datos y documentación interactiva generada a partir del código.

Una de sus principales características es la integración con Pydantic, que permite definir modelos de entrada y salida con validación estructurada. Esto reduce errores comunes en APIs donde los datos llegan con tipos incorrectos, campos faltantes o formatos inesperados.

FastAPI está construido sobre Starlette para la capa web y utiliza ASGI como estándar de ejecución. Esto le permite trabajar de forma natural con programación asíncrona utilizando async y await.

La asincronía es especialmente útil cuando una API realiza operaciones I/O-bound, como consultas a bases de datos, llamadas a servicios externos o acceso a archivos. Mientras una operación espera una respuesta externa, el event loop puede atender otras solicitudes.

Sin embargo, utilizar async no mejora automáticamente tareas CPU-bound. Procesos pesados de cálculo, compresión o machine learning pueden seguir bloqueando el event loop si se ejecutan directamente en la misma tarea.

FastAPI también genera documentación automática mediante OpenAPI. Por defecto, una aplicación puede exponer interfaces interactivas como Swagger UI y ReDoc, facilitando la exploración y prueba de endpoints.

En arquitecturas de producción, FastAPI suele desplegarse detrás de un servidor ASGI como Uvicorn o Gunicorn con workers adecuados. También puede integrarse con sistemas de caché como Redis y bases de datos relacionales como PostgreSQL.

Para aplicaciones con muchos usuarios concurrentes, es importante controlar correctamente conexiones, pools de base de datos, timeouts y límites de concurrencia. Una mala configuración puede provocar latencia elevada aunque el framework sea asíncrono.