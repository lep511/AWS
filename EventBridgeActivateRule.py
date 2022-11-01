import boto3
import json
import argparse

parser = argparse.ArgumentParser(description='Activate CloudWatch Event Rule')

# Activate eventbridge rules

client = boto3.client('events')

def activate_rule(rule_name):
    response = client.enable_rule(
        Name=rule_name
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Rule {} activated\n".format(rule_name))
    else:
        print("Error activating rule {}\n".format(rule_name))

if __name__ == "__main__":
    parser.add_argument('--rule_name', '-r', required=True, help='EventBrdige Event Rule Name')
    args = parser.parse_args()
    activate_rule(args.rule_name)
