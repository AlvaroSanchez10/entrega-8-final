# PostgreSQL

PostgreSQL es un sistema de gestión de bases de datos relacional de código abierto utilizado para almacenar información estructurada y persistente.

Soporta transacciones ACID, relaciones entre tablas, índices, restricciones, vistas, funciones y consultas SQL complejas. Estas capacidades lo convierten en una opción frecuente para aplicaciones que necesitan integridad y consistencia de datos.

Las transacciones permiten agrupar múltiples operaciones de manera que se completen todas juntas o se reviertan si ocurre un error. Esto es importante en procesos como pagos, movimientos contables o actualizaciones relacionadas entre varias tablas.

PostgreSQL soporta distintos tipos de índices. Un índice puede acelerar consultas, aunque también tiene un costo de almacenamiento y escritura. Crear índices sin criterio puede perjudicar el rendimiento en operaciones de inserción y actualización.

En aplicaciones web concurrentes es importante administrar correctamente las conexiones. Abrir una nueva conexión para cada solicitud puede generar sobrecarga. Por eso se utilizan pools de conexiones que reutilizan conexiones existentes.

Cuando el número de conexiones supera la capacidad configurada, pueden aparecer errores de conexión, esperas prolongadas o degradación del rendimiento.

PostgreSQL suele utilizarse junto con Redis. PostgreSQL mantiene la fuente persistente y consistente, mientras Redis puede acelerar lecturas repetidas mediante caché.

También es importante monitorear consultas lentas, locks, uso de índices y consumo de recursos. Una consulta mal optimizada puede convertirse en un cuello de botella incluso cuando la infraestructura dispone de suficiente capacidad.