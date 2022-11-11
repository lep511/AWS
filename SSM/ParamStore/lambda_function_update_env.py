# Policy needed for the Lambda function:
# ssm:GetParameter
# ssm:PutParameter
# ssm:DescribeParameters
# lambda:UpdateFunctionConfiguration

import json
import os
import boto3
import logging

list_functions_parameter = os.environ['PAR_LIST_FUNCTIONS']
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    lambda_client = boto3.client('lambda')
    client = boto3.client('ssm')
    status_code = 200
    message = 'Success!'
    
    json_event = json.dumps(event)
    print("[INFO] event: " + json_event)
    
    parameterName = event['detail']['name']
    
    # Get the bucket name from the SSM parameter
    try:
        response = client.get_parameter(
            Name=parameterName,
            WithDecryption=False
        )
    except Exception as e:
        logger.error(e)
        status_code = 500
        message = 'Error getting parameter: {}'.format(parameterName)
    else:
        bucket_name = response["Parameter"]["Value"]
        
    # Get the list of functions from the SSM parameter
    if status_code == 200:
        try:
            response = client.get_parameter(
                Name=list_functions_parameter,
                WithDecryption=False
            )   
        except Exception as e:
            logger.error(e)
            status_code = 500
            message = 'Error getting parameter: {}'.format(list_functions_parameter)
        else:
            list_functions = response["Parameter"]["Value"]
            list_functions = list_functions.replace(" ", "").split(",")
            logger.info(list_functions)
        
        for function in list_functions:
            try:
                response = lambda_client.update_function_configuration(
                    FunctionName=function,
                    Environment={
                        'Variables': {
                            'BUCKET_NAME': bucket_name
                        }
                    }
                )
            except Exception as e:
                logger.error(e)
                status_code = 500
                message = 'Error updating function: {}'.format(function)
            
    return {"statusCode": status_code, "body": json.dumps({"message": message})}
    