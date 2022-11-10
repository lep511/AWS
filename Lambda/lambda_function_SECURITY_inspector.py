# Se le ha asignado la tarea de configurar un correo electrónico de resumen semanal 
# para resaltar los puntos de datos clave de Inspector. Como punto de partida, el 
# correo electrónico debe resaltar las vulnerabilidades 
# que afectan a la mayoría de las instancias e imágenes.

import boto3
import json
import os
import logging

# SNSTopic: The arn of the topic to which you want to send the SNS notification
SNSTopicARN = os.getenv('SNSTopic')
if SNSTopicARN is None:
    logger.error('SNSTopic is not set')
    raise Exception('SNSTopic is not set')

logger = logging.getLogger()
inspector2 = boto3.client('inspector2')
sns = boto3.client('sns')


def lambda_handler(event, context):
    

    
    response = inspector2.list_finding_aggregations(
        aggregationType = 'PACKAGE',
        maxResults = 5,
        aggregationRequest={
            'packageAggregation': {
                'sortBy': 'CRITICAL',
                'sortOrder': 'DESC'
            }
        }
    )
        
    print(response)
    
    msg = "Vulnerabilities impacting the most instances and images.\n\n"
    
    for i in range(len(response['responses'])):
        package_name = response['responses'][i]['packageAggregation']['packageName']
        count_critical = response['responses'][i]['packageAggregation']['severityCounts']['critical']
        count_high = response['responses'][i]['packageAggregation']['severityCounts']['high']
        count_medium = response['responses'][i]['packageAggregation']['severityCounts']['medium']

        msg += "* Package: {} \n".format(package_name)
        msg += "    Counts of findings by severity:\n"
        msg += "      Critical: {} \n".format(count_critical)
        msg += "      High: {} \n".format(count_high)
        msg += "      Medium: {} \n\n".format(count_medium)
    
    try:
        sns.publish(
            TopicArn=SNSTopicARN,
            Subject='Weekly Vulnerability Report',
            Message=msg
        )
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 400,
            'body': json.dumps('Error publishing to SNS')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Success publishing to SNS')
        }
    
          