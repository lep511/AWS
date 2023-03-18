import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

output_table = os.environ.get('OUTPUT_TABLE_NAME')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

def handler(event, context):
    table = dynamodb.Table(output_table)
    
    ddb_response = table.scan(FilterExpression=Attr('anomaly_score').gte('2'))
    
    items = ddb_response['Items']

    for item in items:
        location = item['location']
        wind_speed = item['wind_speed']
        
        message = f'''\
                Abnormal wind turbine speed detected for {location} with a wind speed of {wind_speed}.
        
                NOTE: As per National Wind Watch, every wind turbine has a range of wind speeds, typically around 30 to 55 mph, in which it will produce maximum capacity. 
                      When wind is more than 70 mph, it is important to start shutdown procedures in order to protect the turbine from high wind.'''
       
        sns_response = sns.publish(
            TargetArn=sns_topic_arn,
            Message=(message),
            Subject='Abnormal Wind Turbine Speed Detected'
        )
        
        print('Abnormal wind turbine speed detected for ' + location + ' with a wind speed of ' + wind_speed + ' .')