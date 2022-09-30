# The following is example Python code that receives Kinesis event record data as input and processes it. 
# For illustration, the code writes to some of the incoming event data to CloudWatch Logs.
#
# NOTE: To process events from Amazon Kinesis, iterate through the records included in the event object 
#       and decode the Base64-encoded data included in each.

from __future__ import print_function
#import json
import base64
def lambda_handler(event, context):
    for record in event['Records']:
       #Kinesis data is base64 encoded so decode here
       payload=base64.b64decode(record["kinesis"]["data"])
       print("Decoded payload: " + str(payload))