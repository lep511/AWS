import os
import boto3
import json
import random

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
    counter = 0

    for i in range(50):
        item = {
            "Location": str(random.randint(10000, 99999)),
            "SKU": random.choice(["ItemX", "ItemY", "ItemZ"]),
            "StockLevel": random.randint(1, 10),
            "ReplenishAmount": random.randint(10, 30),
            "ReplenishBelow": random.randint(1, 3)
        }

        #Put the item into the table
        try:
            table.put_item(Item=item)
            counter += 1
        except Exception as e:
            print("Unable to add item: ", item)
            continue

    return {
        "statusCode": 200,
        "body": json.dumps("{} items added to the table".format(counter))
    }
