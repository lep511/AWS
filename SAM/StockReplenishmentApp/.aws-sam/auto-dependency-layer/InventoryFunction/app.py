import json
import os
import boto3

INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]
EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

def update_inventory(location, sku, count):
    dynamodb = boto3.client("dynamodb")
    result = dynamodb.update_item(
        TableName=INVENTORY_TABLE,
        Key={
            'Location': { "S" : location },
            'SKU': { "S" : sku }
        },
        UpdateExpression='SET StockLevel = StockLevel + :incr',
        ExpressionAttributeValues={":incr":{"N": str(count)}},
        ReturnValues="UPDATED_NEW"
    )
    new_level = result['Attributes']['StockLevel']['N']

    # raise a stocklevel changed event
    eventbridge = boto3.client('events')
    eventbridge.put_events(
        Entries=[
            {
                'Source': 'StockApp',
                'DetailType': 'StockLevel',
                'Detail': json.dumps({
                    "Location" : location,
                    "SKU" : sku,
                    "StockLevel" : new_level
                }),
                'EventBusName': EVENT_BUS_NAME
            },
        ]
    )

def lambda_handler(event, context):
    detail_type = event["detail-type"]
    location = event["detail"]["Location"]
    sku = event["detail"]["SKU"]

    if detail_type == "Purchase":
        purchase_count = int(event["detail"]["PurchaseCount"])
        update_inventory(location, sku, purchase_count * -1)
    elif detail_type == "Replenish":
        repenish_count = int(event["detail"]["ReplenishCount"])
        update_inventory(location, sku, repenish_count)

    return {
        "statusCode": 200,
        "headers": { "access-control-allow-origin": "*" },
        "body": json.dumps({
            "message": "event processed"
        }),
    }