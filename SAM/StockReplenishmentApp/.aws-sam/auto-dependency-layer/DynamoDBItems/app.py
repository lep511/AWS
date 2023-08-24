import os
import boto3
import json

INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]

def send_response(event, context, response_status, response_data):
    response_body = json.dumps({
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    })

    headers = {
        "Content-Type": "",
        "Content-Length": str(len(response_body))
    }

    response = requests.put(event['ResponseURL'], data=response_body, headers=headers)
    print(f"Status code: {response.status_code}, response text: {response.text}")

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(INVENTORY_TABLE)

    item = {
        "Location": "90210",
        "SKU": "ItemX",
        "StockLevel": 5,
        "ReplenishAmount": 10,
        "ReplenishBelow": 3
    }

    #Put the item into the table
    table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": "Item added to the table"
    }
