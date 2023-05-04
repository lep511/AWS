## SEGURIDAD API MULTICAPA CON COGNITO Y WAF

<br>

![image](https://wellarchitectedlabs.com/Security/300_Multilayered_API_Security_with_Cognito_and_WAF/Images/section3/section3-security_enhanced_architecture.png)

**[Link: Level 300: Multilayered API Security with Cognito and WAF](https://wellarchitectedlabs.com/security/300_labs/300_multilayered_api_security_with_cognito_and_waf/)**

### Introducción
Las API se utilizan para la integración entre aplicaciones y ayudan a nuestros clientes a ofrecer nuevos negocios digitales como API públicas en ecosistemas de socios. Debido a la naturaleza pública de estas API, la seguridad es una de las principales preocupaciones de todas las organizaciones que buscan desarrollar API para aumentar sus modelos de negocio existentes. Aunque la seguridad de las API se beneficia ahora de una mayor concienciación y cobertura de las funciones de los productos, los responsables de las aplicaciones deben crear y aplicar una estrategia eficaz de seguridad de las API que se ajuste a sus necesidades empresariales. Un ejemplo de enfoque eficaz para proteger una API es adoptar una estrategia de confianza cero que garantice que sólo las solicitudes autorizadas puedan acceder a la capa empresarial de su aplicación. Además, evaluar la confianza en varias capas de la arquitectura permite realizar varias comprobaciones a medida que los datos de la API transitan por la carga de trabajo.

Mediante el uso de AWS Cognito, es posible crear grupos de usuarios que trabajen con su API para obtener un token de acceso de identidad para el usuario, que luego se puede utilizar para aplicar controles de autorización en su capa de API. Sin embargo, no solo los usuarios legítimos pueden exponer potencialmente a su organización a un alto riesgo, sino que también pueden producirse ataques con credenciales o tokens válidos. Para mitigar este riesgo, AWS Cognito le permite configurar cuánto tiempo será válido el token de acceso y la integración de Amazon WAF junto con CloudFront le permitirá añadir otra capa de seguridad de API para lograr un nivel de protección sólido.

### Lanzar la infraestructura base

Para compilar y desplegar su aplicación por primera vez, ejecute lo siguiente en su shell:

```bash
sam build
sam deploy --guided
```

Luego ejecute:

```bash
python send_requests.py <APIGatewayURL>
```

## IMPEDIR QUE LAS SOLICITUDES ACCEDAN DIRECTAMENTE A LA API

Al integrar CloudFront con puntos de enlace de API regionales, el servicio no solo distribuye el tráfico entre varias ubicaciones de borde para mejorar el desempeño, sino que también admite el geobloqueo, que puede utilizar para ayudar a bloquear solicitudes de ubicaciones geográficas concretas para que no se sirvan. Con Amazon CloudFront, también puede imponer conexiones cifradas de extremo a extremo a una API de origen mediante HTTPS. Además, CloudFront puede cerrar automáticamente las conexiones de atacantes de lectura lenta o escritura lenta. A continuación, API Gateway se puede configurar para que solo acepte solicitudes procedentes de CloudFront. Esto ayuda a evitar que alguien acceda directamente a su implementación de API Gateway. En esta sección del laboratorio, utilizará un valor de encabezado personalizado de CloudFront generado por AWS Secrets Manager en combinación con AWS WAF.

```bash
sam build --template-file cloudfront-cognito.yaml
sam deploy --template-file cloudfront-cognito.yaml --guided
```

Vaya a la sección Outputs de la pila de cloudformation anterior que utilizó para desplegar la infraestructura de laboratorio base. Copie y pegue **APIGatewayURL**. Los demás valores pueden dejarse por defecto. El despliegue puede tardar entre 3 y 4 minutos.