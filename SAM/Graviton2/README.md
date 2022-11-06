# AWS Lambda en Graviton2

AWS Lambda ahora le permite configurar funciones nuevas y existentes para que se ejecuten en procesadores AWS Graviton2 basados en Arm, además de las funciones basadas en x86. El uso de esta opción de arquitectura de procesador le permite obtener un rendimiento superior de hasta un 34%. Los cargos por duración, facturados con granularidad de milisegundos, son un 20% más bajos en comparación con los precios actuales de x86. Esto también se aplica a los cargos de duración cuando se utiliza Provisioned Concurrency. Compute Savings Plans es compatible con las funciones Lambda impulsadas por Graviton2.

El cambio de arquitectura no afecta a la forma en que se invocan las funciones ni a la forma en que comunican sus respuestas. Las integraciones con APIs, servicios, aplicaciones o herramientas no se ven afectadas por la nueva arquitectura y siguen funcionando como antes. Los siguientes tiempos de ejecución, que utilizan Amazon Linux 2, son compatibles con Arm:

* Node.js 12 y 14
* Python 3.8 y 3.9
* Java 8 (java8.al2) y 11
* .NET Core 3.1
* Ruby 2.7
* Tiempo de ejecución personalizado (provided.al2)

## Uso de contenedores

En AWS re:Invent 2020, AWS Lambda lanzó el soporte de imágenes de contenedor para las funciones de Lambda. Esta nueva característica permite a los desarrolladores empaquetar e implementar funciones de Lambda como imágenes de contenedor de hasta 10 GB de tamaño. AWS SAM también ha añadido soporte para administrar, crear e implementar funciones de Lambda mediante imágenes de contenedor.