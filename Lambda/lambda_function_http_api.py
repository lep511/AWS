import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import logging
import json

# AWS Lambda Function Logging in Python - https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.Session()
dynamodb = session.resource("dynamodb")

table_name = "data-flow"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
	logger.info(event)

	try:
		route_key = event['routeKey']
	except Exception as e:
		print(e)
		raise e

	if route_key == "DELETE /items/{id}":
		value_id = event['pathParameters']['id']
		delete_item(value_id)
		message = "Item deleted."

	elif route_key == "GET /items/{id}":
		value_id = event['pathParameters']['id']
		message = get_item(value_id)

	return {
		'statusCode': 200,
		'message': json.dumps(message)
	}


def delete_item(value_id):
	try:
		ret = table.delete_item(Key={'id': value_id})
		logger.info({"operation": "delete item: " + str(value_id)})

	except ClientError as err:
		print(err)
		logger.debug({"operation": "delete item", "details": err})


def get_item(id):
	try:
		ret = table.get_item(
			Key={ 'id': id }
		)
		logger.info({"operation": "query an item ", "details": ret})
		return ret['Item']
	except ClientError as err:
		logger.debug({"operation": "item query", "details": err})