import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FORCE_ERROR_ATTRIBUTE_KEY = 'force-error'

def lambda_handler(event, context):
  logger.info("Received event: {}".format(json.dumps(event, indent=2)))
  event_detail = event['detail']


  if (FORCE_ERROR_ATTRIBUTE_KEY in event_detail['OrderDetails'] and event_detail[FORCE_ERROR_ATTRIBUTE_KEY]):
    error_message = 'FAILED! (force-error == true)'
    logger.error(error_message)
    raise Exception(error_message)

  return event_detail