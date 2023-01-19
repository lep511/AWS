import json
import boto3

def lambda_handler(event, context):
    print(event)

    client = boto3.client('ssm')

    create_opsitem = client.create_ops_item(
        Description='Datawrite service is failing to write data to S3',
        OperationalData={
            '/aws/resources': {
                'Value': '[{\"arn\":\"arn:aws:s3:::well-architected-labs-54898\"}]',
                'Type': 'SearchableString'
            }
        },
        Source='Lambda',
        Category='Availability',
        Title='S3 Data Writes failing',
        Severity='2'
    )

    print(create_opsitem)

    return {
        'statusCode': 200,
        'body': json.dumps('OpsItem Created!')
    }