# APIs REST privadas sin servidor con AWS Lambda usando SAM

## Crear rápidamente microservicios sin servidor utilizando Lambda

Al utilizar Amazon API Gateway, es posible crear rápidamente microservicios sin servidor respaldados por Lambda. Revisaremos uno de estos despliegues y utilizaremos el modelo de aplicación sin servidor de AWS (SAM) para implementarlo.

### Introducción

Con los sistemas en la nube en constante crecimiento, muchas empresas han optado por abandonar los monolitos y adoptar una arquitectura distribuida compuesta por microservicios. AWS permite el desarrollo de dichos servicios sin necesidad de gestionar la infraestructura de servidores subyacente.

Repasaremos un enfoque de infraestructura como código (IaC) para desplegar uno de estos servicios utilizando SAM. El despliegue asumirá que ya existe un clúster privado virtual (VPC) y que sólo las máquinas virtuales en subredes específicas dentro del clúster deberían poder acceder al servicio privado. También asumiremos que el desarrollador ya tiene las herramientas necesarias de AWS SAM instaladas localmente.

### Archivos y carpetas

La carpeta cmd contendrá nuestros scripts de ayuda para el despliegue y la depuración local de nuestra función, como se muestra a continuación:

**debug.sh**: Ejecuta la función en el ordenador local utilizando test-event.json como entrada.

**deploy.sh**: Despliega el servicio en AWS.

La carpeta src contendrá el código fuente de Lambda. En este caso, consiste en los archivos Node index.js y package.json. Sin embargo, la misma técnica que se mostrará aquí funcionaría también con cualquiera de los otros lenguajes Lambda soportados.

**test-event.json**: Contiene una muestra del objeto de solicitud que será proxyado por API Gateway a la función. Esto es utilizado por nuestro debug.sh cuando se prueba la función localmente y puede ser un gran ahorro de tiempo al eliminar el requisito de desplegar después de cada cambio.

**template.yaml**: Contiene la plantilla de despliegue de nuestra función Lambda que es invocada por una puerta de enlace de la API accesible sólo desde una VPC ya existente. 

### Lanzar aplicación

Para desplegar nuestra pila de servicios, basta con ejecutar el script: `deploy.sh`

Durante el despliegue, te aparecerá el mensaje "MyServelessLambdaFunction puede no tener definida la autorización. ¿Está bien?" Esto es de esperar ya que no hemos implementado la autorización.

### Conclusión

Hemos visto cómo crear un microservicio de API sin servidor utilizando Amazon API Gateway y Lambda. El servicio completo se describe en un único archivo de plantilla y se puede desplegar de forma programática.






