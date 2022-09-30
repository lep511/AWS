# Uso de ADOT para instrumentar las funciones de Python

ADOT proporciona capas de Lambda completamente administradas que empaquetan todo lo necesario para recopilar datos de telemetría mediante el OTel SDK. Utilizando esta capa, se pueden instrumentar las funciones de Lambda sin tener que modificar el código de ninguna función. También se puede configurar la capa para que realice una inicialización personalizada de OTel. Para obtener más información, consulte Configuración personalizada del recopilador de ADOT en Lambda en la documentación de ADOT.

Para los tiempos de ejecución de Python, puede agregar la capa Lambda administrada por AWS para ADOT Python para instrumentar automáticamente sus funciones. Esta capa funciona para arquitecturas arm64 y x86_64. Para obtener instrucciones detalladas sobre cómo agregar esta capa, consulte Soporte de Lambda de AWS Distro for OpenTelemetry para Python en la documentación de ADOT.

## Activación del seguimiento con la consola de Lambda

**Para activar el seguimiento activo**

* Abra la página de Functions (Funciones) en la consola de Lambda.

* Elija una función.

* Elija Configuration (Configuración), y luego Monitoring and operations tools (Herramientas de supervisión y operaciones).

* Elija Edit (Editar).

* En X-Ray, active Active tracing (Rastreo activo).

* Seleccione Save.