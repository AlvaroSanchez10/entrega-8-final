# Redis

Redis es un sistema de almacenamiento de datos en memoria ampliamente utilizado como caché, almacén de sesiones, cola de mensajes y mecanismo de coordinación distribuida.

Al mantener los datos principalmente en memoria, Redis puede ofrecer tiempos de respuesta muy bajos. Esto lo hace útil para información que se consulta con mucha frecuencia y cuya obtención desde una base de datos principal sería más costosa.

Una arquitectura común utiliza PostgreSQL como fuente persistente y Redis como capa de caché. Cuando una aplicación necesita un dato, primero consulta Redis. Si el dato está disponible, puede responder sin acceder a PostgreSQL. Si no está disponible, consulta la base principal y luego guarda el resultado temporalmente en Redis.

Este patrón reduce la carga sobre la base de datos y puede mejorar significativamente la latencia.

Redis trabaja con estructuras de datos como strings, hashes, listas, sets y sorted sets. Estas estructuras permiten resolver diferentes tipos de problemas sin depender exclusivamente de claves y valores simples.

También puede utilizarse para manejar sesiones de usuarios, rate limiting y colas simples.

El rate limiting puede implementarse mediante contadores que expiran después de un periodo. Por ejemplo, una API puede registrar cuántas solicitudes realizó un usuario durante un minuto y bloquear temporalmente nuevas solicitudes cuando supera cierto límite.

Es importante definir políticas de expiración. Si una caché almacena información indefinidamente, puede devolver datos obsoletos. Por eso se utilizan TTLs para controlar cuánto tiempo permanece una entrada válida.

Redis no debe considerarse automáticamente un reemplazo de una base relacional. Su fortaleza está en la velocidad y en casos donde el acceso en memoria aporta beneficios claros.