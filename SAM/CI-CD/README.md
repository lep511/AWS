## AWS SAM Pipelines
### Genere automáticamente canalizaciones de implementación para aplicaciones sin servidor

#### [Link](https://aws.amazon.com/es/blogs/compute/introducing-aws-sam-pipelines-automatically-generate-deployment-pipelines-for-serverless-applications/)

AWS SAM Pipelines facilita la creación de canalizaciones de integración e implementación continuas (CI/CD) seguras para el sistema de integración e implementación continuas (CI/CD) preferido de su organización.

Canalizaciones de AWS SAM
Una canalización de implementación es una secuencia automatizada de pasos que se realizan para lanzar una nueva versión de una aplicación. Se definen mediante un archivo de plantilla de canalización. AWS SAM Pipelines proporciona plantillas para sistemas CI/CD populares como AWS CodePipeline, Jenkins, GitHub Actions y GitLab CI/CD. Las plantillas de canalizaciones incluyen prácticas recomendadas de implementación de AWS para ayudar con las implementaciones multicuenta y multirregión. Los entornos de AWS, como los de desarrollo y producción, suelen existir en diferentes cuentas de AWS. Esto permite a los equipos de desarrollo configurar canalizaciones de implementación seguras, sin realizar cambios involuntarios en la infraestructura. También puede suministrar sus propias plantillas de canalizaciones personalizadas para ayudar a estandarizar las canalizaciones entre los equipos de desarrollo.

AWS SAM Pipelines se compone de dos comandos:

* `sam pipeline bootstrap`, un comando de configuración que crea los recursos de AWS necesarios para crear una canalización.

* `sam pipeline init`, un comando de inicialización que crea un archivo de canalización para su sistema CI/CD preferido. Por ejemplo, un archivo Jenkinsfile para Jenkins o un archivo .gitlab-ci.yml para GitLab CI/CD.
Tener dos comandos separados le permite gestionar las credenciales para operadores y desarrolladores por separado. Los operadores pueden utilizar sam pipeline bootstrap para aprovisionar los recursos de pipeline de AWS. Esto puede reducir el riesgo de errores de producción y los costes operativos. Los desarrolladores pueden centrarse en la construcción sin tener que configurar la infraestructura de canalización ejecutando el comando sam pipeline init.

También puede combinar estos dos comandos ejecutando sam pipeline init -bootstrap. Esto le lleva a través de todo el bootstrap guiada y el proceso de inicialización.