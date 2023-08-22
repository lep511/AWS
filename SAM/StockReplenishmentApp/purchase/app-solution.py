import json
import os
import boto3

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

def lambda_handler(event, context):
    eventbridge = boto3.client('events')
    # write a purchase event to the eventbus
    location = event["queryStringParameters"]["Location"]
    sku = event["queryStringParameters"]["SKU"]
    purchaseCount = event["queryStringParameters"]["PurchaseCount"]

    eventbridge.put_events(
        Entries=[
            {
                'Source': 'StockApp',
                'DetailType': 'Purchase',
                'Detail': json.dumps({
                    "Location" : location,
                    "SKU" : sku,
                    "PurchaseCount" : purchaseCount
                }),
                'EventBusName': EVENT_BUS_NAME
            },
        ]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "purchase event created"
        })
    }
