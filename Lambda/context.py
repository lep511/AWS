import json
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):   
    logger.info("Lambda function ARN:" + context.invoked_function_arn)
    logger.info("CloudWatch log stream name:" + context.log_stream_name)
    logger.info("CloudWatch log group name:" +  context.log_group_name)
    logger.info("Lambda Request ID:" + context.aws_request_id)
    logger.info("Lambda function memory limits in MB:" + context.memory_limit_in_mb)

    # We have added a 1 second delay so you can see the time remaining in get_remaining_time_in_millis.
    time.sleep(1) 
    logger.info("Lambda time remaining in MS:" + str(context.get_remaining_time_in_millis()))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

"""
Propiedades de context

    * get_remaining_time_in_millis: devuelve el número de milisegundos que quedan antes del tiempo de espera de la ejecución.

    * function_name: el nombre de la función de Lambda.

    * function_version: la versión de la función.

    * invoked_function_arn: el nombre de recurso de Amazon (ARN) que se utiliza para invocar esta función. Indica si el invocador especificó un número de versión o alias.

    * memory_limit_in_mb: cantidad de memoria asignada a la función.

    * aws_request_id: el identificador de la solicitud de invocación.

    * log_group_name: grupo de registros de para la función.

    * log_stream_name: el flujo de registro de la instancia de la función.

    * identity: (aplicaciones móviles) Información acerca de la identidad de Amazon Cognito que autorizó la solicitud.

        * cognito_identity_id: la identidad autenticada de Amazon Cognito.

        * cognito_identity_pool_id: el grupo de identidad de Amazon Cognito que ha autorizado la invocación.

    * client_context: (aplicaciones móviles) Contexto de cliente proporcionado a Lambda por la aplicación cliente.

        * client.installation_id

        * client.app_title

        * client.app_version_name

        * client.app_version_code

        * client.app_package_name

        * custom: un elemento dict de valores personalizados establecidos por la aplicación cliente para móviles.

        * env: un elemento dict de información de entorno proporcionado por el AWS SDK.
"""