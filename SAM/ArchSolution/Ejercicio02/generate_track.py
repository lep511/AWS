import argparse
import boto3
import json
import random
from datetime import datetime

kinesis = boto3.client('firehose')

def get_now_data():
    now_date = datetime.now().isoformat()
    now_format = datetime.strptime(now_date, '%Y-%m-%dT%H:%M:%S.%f')
    return now_format.strftime('%Y-%m-%d %H:%M:%S')

def get_data():
    return {
        'EVENT_TIME': get_now_data(),
        'TICKER_SYMBOL': random.choice(['AAPL', 'AMZN', 'MSFT', 'INTC', 'TBV']),
        'SECTOR': random.choice(['TECH', 'FINANCE', 'HEALTHCARE', 'REAL_ESTATE', 'UTILITIES']),
        'CHANGE': round(random.uniform(-1, 1), 2),
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
    parser.add_argument('--repeat', type=int, default=50, help='Number of records to generate')
    args = parser.parse_args()

    list_strams = kinesis.list_delivery_streams()['DeliveryStreamNames']
    count_stream = len(list_strams)
    
    if count_stream == 1:
        print('Generating {} records to stream {}...'.format(args.repeat, list_strams[0]))
        index_stream = list_strams[0]

    elif count_stream > 1:
        print('Found more than one stream...')
        print('Please select one of the following streams:')
        for i in range(count_stream):
            print('  {}. {}'.format(i, list_strams[i]))
        while True:
            try:
                stream_index = int(input('\nEnter the number of the stream you want to use: '))
            except ValueError:
                print('Please enter a number')
                continue
            if stream_index in range(count_stream):
                break
            else:
                print('Invalid index')
            print('\n')
            for i in range(count_stream):
                print('  {}. {}'.format(i, list_strams[i]))
        index_stream = list_strams[stream_index]
    else:
        raise Exception('No streams found')
    
    print('Generating {} records to stream {}...'.format(args.repeat, index_stream))
    generate(index_stream, kinesis, args.repeat)