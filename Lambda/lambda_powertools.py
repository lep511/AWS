import json
import logging
from aws_lambda_powertools.logging.logger import set_package_logger
import os

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics


from boto3.dynamodb.conditions import Key

#set_package_logger() #this will configure our aws_lambda_powertools logger with debug.
logger = Logger()
tracer = Tracer()
metrics = Metrics()

dynamodb = boto3.resource("dynamodb")

if 'TABLE_NAME' in os.environ:
    table = os.environ['TABLE_NAME']
    logger.info("Initializing DDB Table %s", table)
    table = dynamodb.Table(table)
else:
    logger.exception("Variable TABLE_NAME not defined")
    raise EnvironmentError("Variable TABLE_NAME not defined")

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler

def lambda_handler(event, context):
    """
    Update cart table to use user identifier instead of anonymous cookie value as a key. This will be called when a user
    is logged in.
    """
    logger.debug(event)
    cart_id, _ = get_cart_id(event["headers"])

    try:
        # Because this method is authorized at API gateway layer, we don't need to validate the JWT claims here
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError:
        logger.warn("Invalid user tried to check out cart")
        return {
            "statusCode": 400,
            "headers": get_headers(cart_id),
            "body": json.dumps({"message": "Invalid user"}),
        }

    # Get all cart items belonging to the user's identity
    response = table.query(
        KeyConditionExpression=Key("pk").eq(f"user#{user_id}")
        & Key("sk").begins_with("product#"),
        ConsistentRead=True,  # Perform a strongly consistent read here to ensure we get correct and up to date cart
    )

    cart_items = response.get("Items")
    # batch_writer will be used to update status for cart entries belonging to the user
    with table.batch_writer() as batch:
        for item in cart_items:
            # Delete ordered items
            batch.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})

    metrics.add_metric(name="CartCheckedOut", unit="Count", value=1)
    logger.info({"action": "CartCheckedOut", "cartItems": cart_items})

    return {
        "statusCode": 200,
        "headers": get_headers(cart_id),
        "body": json.dumps(
            {"products": response.get("Items")}, default=handle_decimal_type
        ),
    }
