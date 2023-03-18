import boto3
import random
import os
import socket
import time
from sys import exit
import json
import string
import random
from random import randint
from fpdf import FPDF

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sts = boto3.client('sts')
tagging = boto3.client('resourcegroupstaggingapi')

caller = sts.get_caller_identity()
account_number = caller['Account']

session = boto3.session.Session()
aws_region = session.region_name

queueUrl = 'https://sqs.{0}.amazonaws.com/{1}/tickets-queue'.format(aws_region, account_number)
s3bucketwithtags = tagging.get_resources(TagFilters=[{'Key': 'Project','Values':['Spotlight']}],ResourceTypeFilters=['s3']) 
s3_bucket_arn = s3bucketwithtags['ResourceTagMappingList'][0]['ResourceARN']
s3_bucket = s3_bucket_arn.split(':::')[1]

while True:
    response = sqs.receive_message(
        QueueUrl=queueUrl,
        MaxNumberOfMessages=1
    )

    message_in_response =  "Messages" in response
    #print(message_in_response)
    if message_in_response == False:
        time.sleep(10)
    else:
        message = response['Messages'][0]['Body']
        receiptHandle = response['Messages'][0]['ReceiptHandle']
        message_json = json.loads(message)

        for _ in range(1):
            opId = randint(500000000, 999999999)
        name = message_json['Name']
        payment = message_json['Payment']
        paydate = message_json['Pdate']
        eventCode = message_json['eventCode']
        confirCode = message_json['Ccode']

        event_table = dynamodb.Table('events')
        getEvent = event_table.get_item(
            Key={
                'eventCode': eventCode
            }
        )
        artist = getEvent['Item']['artist']
        event_date = getEvent['Item']['date']
        venue_code = getEvent['Item']['venue']

        venue_table = dynamodb.Table('venues')
        getVenue = venue_table.get_item(
            Key={
                'code': venue_code
            }
        )
        venue = getVenue['Item']['site']

        class PDF(FPDF):
            def header(self):
                # Logo
                self.image('aws-training.png', 10, 8, 50)
                # Arial bold 15
                self.set_font('Arial', 'B', 15)
                # Move to the right
                self.cell(80)
                # Title
                self.cell(80, 10, 'AWSome Tickets', 1, 0, 'C')
                # Line break
                self.ln(20)

        # Set font
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, 'Name: ' + name, 0, 1, 'L')
        pdf.cell(0, 10, 'Payment method: ' + str(payment), 0, 1, 'L')
        pdf.cell(0, 10, 'Artist: ' + artist, 0, 1, 'L')
        pdf.cell(0, 10, 'Concert date: ' + event_date, 0, 1, 'L')
        pdf.cell(0, 10, 'Venue: ' + venue, 0, 1, 'L')
        pdf.cell(0, 10, 'Confirmation code: ' + confirCode, 0, 1, 'L')
        pdf.cell(0, 10, 'Purchase date: ' + paydate, 0, 1, 'L')
        pdf.output(str(opId) + '.pdf', 'F')

        upload_s3 = s3.upload_file(str(opId) + '.pdf', s3_bucket, str(opId) + '.pdf')

        tickets_table = dynamodb.Table('tickets')
        putItem = tickets_table.put_item(
            Item={
                'opId': opId,
                'name': name,
                'payment': payment,
                'paydate': paydate,
                'eventCode': eventCode,
                'confirCode': confirCode
            }
        )
        deleteMsg = sqs.delete_message(
            QueueUrl=queueUrl,
            ReceiptHandle=receiptHandle
        )

        os.remove(str(opId) + '.pdf')