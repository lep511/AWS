import boto3
import json
from dataclasses import dataclass, field
from uuid import uuid4
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent,
)

@dataclass
class Order:
    doctor: dict
    patient: dict
    appointmentDateTime: str
    order_id: str = field(default_factory=lambda: f"{uuid4()}")

# See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#module-boto3.session
boto3_session = boto3.session.Session()

logger = Logger()

dynamo_clien = boto3.client("dynamodb")
idempotency_table = os.environ.get("IDEMPOTENCY_TABLE_NAME")

persistence_layer = DynamoDBPersistenceLayer(
    table_name=idempotency_table,
    key_attr="id",
    expiry_attr="expires_at",
    in_progress_expiry_attr="in_progress_expires_at",
    status_attr="current_status",
    data_attr="result_data",
    validation_key_attr="validation_key",
    boto3_session=boto3_session
)

config = IdempotencyConfig(
    event_key_jmespath="body",      # what the idempotency cache is based on
    expires_after_seconds=5 * 60,   # how long to store the idempotency record: 5 minutes
)

class OrderError(Exception):
    """Raised when order is invalid"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

@idempotent(persistence_store=persistence_layer, config=config)
def lambda_handler(event: dict, context: LambdaContext) -> str:
    
    if not event.get("body"):
        return {
            "message": "invalid request, can't find body",
            "statusCode": 400,
        }
    
    try:
        order: Order = process_order(event["body"])
        logger.info("Order id", extra={"order_id": order.order_id})
        
        return {
            "order_id": order.order_id,
            "message": "success",
            "statusCode": 200,
        }
        
    except Exception as exc:
        logger.exception("Error creating order", exc_info=exc)
        raise OrderError(f"Error creating order {str(exc)}")

def process_order(event: dict) -> Order:
    # process order
    # write to dynamodb
    dr_service_table = os.environ.get("DR_SERVICE_TABLE_NAME")
    dynamo_client = boto3.client("dynamodb")

    logger.info("Writing to dynamodb", extra={"event": event})
    dynamo_client.put_item(
        TableName=dr_service_table,
        Item={
            "PK": {"S": f"DR#{event['doctor']['doctor_id']}"},
            "SK": {"S": f"ORDER#{event['patient']['patient_id']}"},
            "doctor_name": {"S": event['doctor']['name']},
            "doctor_specialty": {"S": event['doctor']['specialty']},
            "patient_name": {"S": event['patient']['name']},
            "patient_dob": {"S": str(event['patient']['dob'])},
        }
    )
        
    return Order(**event)