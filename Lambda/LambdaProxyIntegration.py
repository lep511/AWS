import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading hello world function')

def test_func(event):

	logger.info('request: ' + json.dumps(event))

	try:
		logger.info('Received name: ' + event['queryStringParameters']['name'])
		name = event['queryStringParameters']['name']
	except:
		name = "you"

	try:
		logger.info('Received city: ' + event['queryStringParameters']['city'])
		city = event['queryStringParameters']['city']
	except:
		city = "World"

	try:
		time_json = json.loads(event["body"])
		time_body = time_json['time']
	except:
		time_body = "day"

	try:
		day_json = json.loads(event["body"])
		day_body = f" Happy {day_json['day']}!"
	except:
		day_body = ""
	
	greeting = f"Good {time_body}, {name} of {city}." + day_body

	return greeting


def lambda_handler(event, context):
	responseCode = 200
	result = test_func(event)

	return {
		'statusCode': responseCode,
		'headers' : {
				"x-custom-header" : "my custom header value"
				},
		'body': json.dumps(result)
	}