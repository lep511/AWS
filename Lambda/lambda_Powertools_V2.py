# arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPython:29
import os
import boto3
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

# environment variables
# POWERTOOLS_SERVICE_NAME: some_name
# POWERTOOLS_METRICS_NAMESPACE: some_namespace
TABLE_NAME = os.getenv('TABLE_NAME', None)
STAGE = os.getenv("STAGE", "dev")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
metrics = Metrics()

@metrics.log_metrics  # ensures metrics are flushed upon request completion/failure
def lambda_handler(event: dict, context: LambdaContext):
    metrics.add_dimension(name="environment", value=STAGE)
    metrics.add_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=1)
    
    table.put_item(
       Item={
            'employId': event['Item']['id'],
            'first_name': event['Item']['first_name'],
            'last_name': event['Item']['last_name'],
            'age': event['Item']['age']
        }
    )
