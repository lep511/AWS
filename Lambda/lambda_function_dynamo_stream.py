import boto3

# This will instantiate DynamoDB client for later use.
dynamodb = boto3.resource('dynamodb')

def check_record_pattern(record):
    if 'dynamodb' in record and 'NewImage' in record['dynamodb']:
        new_image = record['dynamodb']['NewImage']
        return 'improvement' in new_image and 'region' in new_image and 'S' in new_image['improvement'] and 'S' in new_image['region']
    return False

def lambda_handler(event, context):
    # Here you can find the documentation about the event and a sample of the event:
    # https://docs.aws.amazon.com/lambda/latest/dg/with-ddb-example.html
    print("Received Stream Event: " + str(event))
    for record in event['Records']:
        print(record['eventID'])
        print(record['eventName'])

        if check_record_pattern(record):
            improvement = record['dynamodb']['NewImage']['improvement']['S']
            region = record['dynamodb']['NewImage']['region']['S']
            print("Vote for " + improvement + " from region " +region)

            # Below code will enable you to use update_item API to increment 1 vote
            # for a given improvement and region to total_votes table.

            # For UpdateItem expressions check
            # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html
            # For boto3 update_item check
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item

            table = dynamodb.Table('total_votes')
            table.update_item(
                Key={
                    'improvement': improvement,
                    'region': region
                },
                UpdateExpression="ADD total_votes :votevalue",
                ExpressionAttributeValues={
                    ':votevalue': 1
                }
            )
        
    return 'Successfully processed {} records.'.format(len(event['Records']))
