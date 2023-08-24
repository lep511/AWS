import json
import os
import boto3

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

def lambda_handler(event, context):
    print(event)
    eventbridge = boto3.client('events')
    # write a purchase event to the eventbus
    body_data = json.loads(event["body"])
    location = body_data["Location"]
    sku = body_data["SKU"]
    purchaseCount = body_data["PurchaseCount"]

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
