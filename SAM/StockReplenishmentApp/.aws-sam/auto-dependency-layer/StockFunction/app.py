import json
import os
import boto3

INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]

def lambda_handler(event, context):
    print(event)
    body_data = json.loads(event["body"])
    location = body_data["Location"]
    sku = body_data["SKU"]

    dynamodb = boto3.client("dynamodb")
    result = dynamodb.query(
        TableName=INVENTORY_TABLE,
        KeyConditions={
            'Location': { 'AttributeValueList' : [ {"S" : location} ], 'ComparisonOperator': 'EQ' },
            'SKU': { 'AttributeValueList' : [ { "S" : sku } ], 'ComparisonOperator': 'EQ' }
        },
    )

    stock_level = result["Items"][0]["StockLevel"]['N'] if len(result["Items"]) > 0 else None
    return {
        "statusCode": 200,
        "headers": { "access-control-allow-origin": "*" },
        "body": json.dumps({
            "StockLevel": stock_level
        }),
    }