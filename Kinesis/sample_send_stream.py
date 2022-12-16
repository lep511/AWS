import boto3
from botocore import exceptions
import json

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

# Send a strem of data to the Kinesis stream

data_to_send = { 
    "TICKER_SYMBOL": "QXZ",
    "SECTOR": "HEALTHCARE",
    "CHANGE": 0.05,
    "PRICE": 84.51
}

# Send data
n_stream = input("Enter the number of records to send to the stream: ")
print(f"Sending {n_stream} records to stream...")

for i in range(int(n_stream)):
    try:
        response = kinesis_client.put_record(
            StreamName='DataStremData',
            Data=json.dumps(data_to_send),
            PartitionKey='SECTOR'
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            print(f"Error {status_code} sending data to stream")

    except exceptions.ClientError as e:
        print("Error sending data to stream: ", e)

print("Data sent to stream: ", n_stream)
