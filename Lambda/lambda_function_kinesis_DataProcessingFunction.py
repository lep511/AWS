# Creating a Lambda package with runtime dependencies
# https://docs.aws.amazon.com/lambda/latest/dg/python-package-create.html#python-package-create-with-dependency
#
# NOTE: To process events from Amazon Kinesis, iterate through the records included in the event object 
#       and decode the Base64-encoded data included in each.

from datetime import datetime
import pandas as pd
import boto3
import os
import base64


s3 = boto3.client('s3')
data_bucket = os.environ.get('DATA_BUCKET_NAME')


def handler(event, context):
    """Example delivery stream record event
    {
        "invocationId":"00540a87-5050-496a-84e4-e7d92bbaf5e2",
        "applicationArn":"arn:aws:kinesisanalytics:us-east-1:12345678911:application/lambda-test",
        "streamArn":"arn:aws:firehose:us-east-1:AAAAAAAAAAAA:deliverystream/lambda-test",
        "records":[
            {
                "recordId":"49572672223665514422805246926656954630972486059535892482",
                "data":"aGVsbG8gd29ybGQ=",
                "kinesisFirehoseRecordMetadata":{
                    "approximateArrivalTimestamp":1520280173
                }
            }
        ]
    }
    """

    """Example response format
    {
        "records": [
            {
                "recordId": "49572672223665514422805246926656954630972486059535892482",
                "result": "Ok",
                "data": "SEVMTE8gV09STEQ="
            }
        ]
    }
    """

    # Response will be a list of records.
    response = {
        "records": []
    }

    # Clickstream data labels.
    labels = ['prev', 'curr', 'type', 'n']

    # Iterate list of input records.
    for record in event.get('records'):
        records = []

        # Get data from Kinesis record.
        data = base64.b64decode(record.get('data')).decode('utf-8')

        # Split into lines.
        lines = data.split('\n')

        for line in lines:
            # Skip any empty lines.
            if line == "":
                continue

            try:
                cols = line.split('\t')
                records.append((cols[0], cols[1], cols[2], cols[3]))
            except:
                continue

        # Convert to data frame.
        df = pd.DataFrame.from_records(records, columns=labels)

        response['records'].append({
            "recordId": record['recordId'],
            "result": "Ok",
            "data": base64.b64encode(df.to_csv(header=False, index=False).encode('utf-8'))
        })

    return response
