import boto3
import json
import uuid
import datetime

from schema.com_aws_orders.ordernotification import Marshaller
from schema.com_aws_orders.ordernotification import AWSEvent
from schema.com_aws_orders.ordernotification import OrderNotification

# DynamoDB client
dynamodb = boto3.resource('dynamodb')
orderDetailsTable = dynamodb.Table('OrderDetails')

# EventBridge client
eventBridgeClient = boto3.client('events')

def lambda_handler(event, context):
    """Sample Lambda function reacting to EventBridge events

    Parameters
    ----------
    event: dict, required
        Event Bridge Events Format

        Event doc: https://docs.aws.amazon.com/eventbridge/latest/userguide/event-types.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
        The same input event file
    """

    #Deserialize event into strongly typed object
    awsEvent:AWSEvent = Marshaller.unmarshall(event, AWSEvent)
    detail:OrderNotification = awsEvent.detail

    # Print Order Notification event details
    print(detail)

    # New order Id
    orderId = str(uuid.uuid4())

    # Save Order Notification details into DynamoDB table
    response = orderDetailsTable.put_item(
       Item={
             'orderId': orderId,
             'category': detail.category,
             'location': detail.location,
             'value': str(detail.value)
       }
    )
    print(response)

    # Publish Order Processed event
    response = eventBridgeClient.put_events(
       Entries=[
             {
                'Time': datetime.datetime.utcnow(),
                'Source': 'com.aws.forecast',
                'DetailType': 'Order Processed',
                'Detail': json.dumps({'orderId': orderId}),
                'EventBusName': 'Orders'
             }
       ]
    )
    print(response)

    #Make updates to event payload, if desired
    awsEvent.detail_type = "HelloWorldFunction updated event of " + awsEvent.detail_type;

    #Return event for further processing
    return Marshaller.marshall(awsEvent)
