import argparse
import boto3
import json
import random
from datetime import datetime

STREAM_NAME = "xxx-stack-deliverystream"


def get_data():
    return {
        'EVENT_TIME': datetime.now().isoformat(),
        'TICKER': random.choice(['AAPL', 'AMZN', 'MSFT', 'INTC', 'TBV']),
        'PRICE': round(random.random() * 100, 2)}


def generate(stream_name, kinesis_client, repeat=10):
    """
    generate(stream_name, kinesis_client, repeat=10)

    This function generates a set number of random records and writes them to Kinesis.

    Args:
        stream_name: A string representing the name of the Kinesis stream
        kinesis_client: A Kinesis client that is properly configured and authenticated
        repeat: An integer that represents the number of records to generate
    """
    for i in range(repeat):
        data = get_data()
        print(data)
        kinesis_client.put_record(
            DeliveryStreamName=stream_name,
            Record={"Data" : json.dumps(data)}
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kinesis Data Generator')
    parser.add_argument('--stream', type=str, default=STREAM_NAME, help='Kinesis stream name')
    parser.add_argument('--repeat', type=int, default=10, help='Number of records to generate')
    args = parser.parse_args()

    generate(args.stream, boto3.client('firehose'), repeat=args.repeat)