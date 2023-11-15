import boto3
import json
import random
import argparse

table_name = 'Inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def main(total_items):
    for i in range(total_items):
        table.put_item(
            Item={
                'Location': str(random.randint(10000, 99999)),
                'SKU': random.choice(['ItemX', 'ItemY', 'ItemZ', 'ItemA', 'ItemB', 'ItemC']),
                'StockLevel': random.randint(5, 100),
                'ReplenishAmount': random.randint(30, 50),
                'ReplenishBelow': random.randint(5, 20)
            }
        )
    print('Added {} items to table {}'.format(total_items, table_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add items to DynamoDB table')
    parser.add_argument('--count', type=int, help='Number of items to add', default=10)
    args = parser.parse_args()
    main(args.count)
