import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
print("Ok")

FORCE_ERROR_ATTRIBUTE_KEY = 'force-error'

def lambda_handler(event, context):
  logger.info('{}'.format(event))
  response = requests.get('https://api.github.com')

  return response.json()

