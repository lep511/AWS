import json
import os
import boto3

INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]
EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

def lambda_handler(event, context):
    #  {'detail': {'Location': '90210', 'SKU': 'ItemX', 'StockLevel': '7'}}
    location = event["detail"]["Location"]
    sku = event["detail"]["SKU"]

    # find the replenish below amount and replenish amount
    dynamodb = boto3.client("dynamodb")
    result = dynamodb.query(
        TableName=INVENTORY_TABLE,
        KeyConditions={
            'Location': { 'AttributeValueList' : [ {"S" : location} ], 'ComparisonOperator': 'EQ' },
            'SKU': { 'AttributeValueList' : [ { "S" : sku } ], 'ComparisonOperator': 'EQ' }
        },
    )

    if len(result["Items"]) > 0:
        message = "replenishment not needed"
        stock_level = int(result["Items"][0]["StockLevel"]['N'])
        replenish_amount = int(result["Items"][0]["ReplenishAmount"]['N'])
        replenish_below = int(result["Items"][0]["ReplenishBelow"]['N'])

        if stock_level < replenish_below:
            message = "replenishment created"
            eventbridge = boto3.client('events')
            eventbridge.put_events(
                Entries=[
                    {
                        'Source': 'StockApp',
                        'DetailType': 'Replenish',
                        'Detail': json.dumps({
                            "Location" : location,
                            "SKU" : sku,
                            "ReplenishCount" : replenish_amount
                        }),
                        'EventBusName': EVENT_BUS_NAME
                    },
                ]
            )
    else:
        message = "stock not found"




    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message
        })
    }