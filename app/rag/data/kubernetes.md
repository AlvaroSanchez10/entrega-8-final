# Kubernetes

Kubernetes es una plataforma de orquestación de contenedores diseñada para automatizar el despliegue, escalado y operación de aplicaciones distribuidas.

La unidad mínima de ejecución en Kubernetes es el Pod. Un Pod puede contener uno o varios contenedores que comparten recursos de red y almacenamiento.

Los Deployments permiten declarar cuántas réplicas de una aplicación deben existir. Kubernetes intenta mantener ese estado deseado y recrea Pods cuando alguno falla.

Los Services proporcionan una forma estable de acceder a un conjunto de Pods, incluso cuando las instancias individuales cambian de dirección IP.

Kubernetes también permite definir ConfigMaps y Secrets para separar configuración y credenciales del código de la aplicación.

El escalado puede ser manual o automático. Con Horizontal Pod Autoscaler, Kubernetes puede aumentar o reducir la cantidad de réplicas según métricas como uso de CPU o memoria.

La alta disponibilidad no depende solo de tener múltiples réplicas. También requiere configurar probes de salud, límites de recursos y estrategias de despliegue adecuadas.

Las readiness probes indican si una instancia está lista para recibir tráfico. Las liveness probes ayudan a detectar procesos que quedaron en un estado inválido y deben reiniciarse.

Kubernetes puede integrarse con balanceadores de carga y sistemas de observabilidad. En arquitecturas complejas, logs, métricas y trazas son esenciales para diagnosticar problemas.

Aunque Kubernetes facilita el escalado, también introduce complejidad operacional. Para proyectos pequeños puede ser innecesario, mientras que para sistemas distribuidos de gran escala ofrece herramientas valiosas para automatizar operaciones.
