import boto3
import os

def lambda_handler(event, context):
    accountid = event['account']
    s3_bucket = os.environ['s3_bucket']
    trail_name = os.environ['trail_name']

    # Creating the Cloutrail Client
    cloudtrail_client = boto3.client('cloudtrail')
    sns_client = boto3.client('sns')

    # Function that updates the CloudWatch Logs Configuration of Trail
    def update_cloudwatch():
        print('arn:aws:iam::{}:role/service-role/management-tools-week'.format(accountid))
        print('arn:aws:logs:us-west-2:{}:log-group:management-tools-week:*'.format(accountid))
        my_session = boto3.session.Session()
        my_region = my_session.region_name
        cloudtrail_client.update_trail(
            Name='management-tools-week',
            CloudWatchLogsLogGroupArn='arn:aws:logs:{}:{}:log-group:management-tools-week:*'.format(my_region, accountid),
            CloudWatchLogsRoleArn='arn:aws:iam::{}:role/service-role/management-tools-week'.format(accountid)
        )
        sns_client.publish(
          TopicArn=os.getenv('topic_arn'),
          Message='CloudWatch Log Group not Configured, Updated Trail with CloudWatch Standard',
          Subject='CloudWatch Group on CloudTrail Misconfigured'
        )
    # Describing the LogWorkshop Trail in our Workshop
    trail = cloudtrail_client.describe_trails(
        trailNameList=[trail_name]
    )
    # Making sure the Trail created an object with data
    if trail and trail.get('trailList',[]):
        # Setting a varilable for the Trail Object
        trail_desc = trail['trailList'][0]

        # If the Bucket Name in the trail doesn't match what we want it will update the trail to the bucket we want
        if trail_desc['S3BucketName'] != s3_bucket:
            cloudtrail_client.update_trail(
                Name = trail_name,
                S3BucketName = s3_bucket
            )
            sns_client.publish(
              TopicArn=os.getenv('topic_arn'),
              Message='Bucket Name was Wrong, Corrected Bucket Name on Trail to Standard',
              Subject='S3 Bucket on CloudTrail Misconfigured'
            )
        # If the Cloud Watch Log Group doesn't exit we will update the trail to include it.
        elif 'CloudWatchLogsLogGroupArn' not in trail_desc:
            update_cloudwatch()
        # If the CloudWatch Log Group doesn't match what we expect it will update it.
        elif trail_desc['CloudWatchLogsLogGroupArn'] != 'arn:aws:logs:us-west-2:{}:log-group:ManagementToolsWeek/CloudTrail:*'.format(accountid):
            update_cloudwatch()
        else:
            print('All Good')
    # If no Trail is returned when describing, we will create the Trail.
    else:
        cloudtrail_client.create_trail(
            Name= trail_name,
            S3BucketName= s3_bucket,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            CloudWatchLogsLogGroupArn='arn:aws:logs:us-west-2:{}:log-group:ManagementToolsWeek/CloudTrail:*'.format(accountid),
            CloudWatchLogsRoleArn='arn:aws:iam::{}:role/CloudTrail_CloudWatchLogs_Role'.format(accountid)
        )
        sns_client.publish(
            TopicArn=os.getenv('topic_arn'),
            Message='No CloudTrail, Created a New Trail to Standard',
            Subject='CloudTrail Didnt Exist'
        )
