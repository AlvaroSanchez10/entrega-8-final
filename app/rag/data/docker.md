# Docker

Docker es una plataforma para empaquetar y ejecutar aplicaciones dentro de contenedores.

Un contenedor incluye la aplicación y las dependencias necesarias para ejecutarla, lo que ayuda a reducir diferencias entre entornos de desarrollo, testing y producción.

Las imágenes de Docker se construyen normalmente a partir de un Dockerfile. Este archivo describe una serie de instrucciones, como la imagen base, instalación de dependencias, copia de archivos y comando de ejecución.

Las imágenes están compuestas por capas. Docker reutiliza capas cuando es posible, lo que puede acelerar builds posteriores.

Una buena práctica es reducir el tamaño de las imágenes utilizando bases livianas y evitando copiar archivos innecesarios.

Los contenedores son procesos aislados, pero comparten el kernel del sistema operativo host. Esto los hace más livianos que máquinas virtuales tradicionales.

Docker también permite definir redes entre contenedores. Por ejemplo, una aplicación FastAPI puede ejecutarse en un contenedor mientras PostgreSQL y Redis se ejecutan en otros.

Con Docker Compose se pueden definir múltiples servicios, redes y volúmenes en un archivo declarativo.

Los volúmenes permiten persistir información fuera del ciclo de vida del contenedor. Esto es importante para bases de datos, ya que eliminar un contenedor no debería implicar perder sus datos.

En producción, Docker suele utilizarse junto con herramientas de orquestación como Kubernetes. Docker empaqueta la aplicación, mientras Kubernetes administra el despliegue, escalado y disponibilidad de múltiples instancias.