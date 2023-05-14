import json
import boto3
import os
import string
import random
secureBucket = os.environ['SECURE_BUCKET']
snsTopicArn = os.environ['TOPIC_ARN']
stV = os.environ['SECURE_TAG_VALUE']

snsc = boto3.client('sns')
s3c = boto3.client('s3')

def getRandom(stringLength=10):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def handler(event, context):
    
    accountId = event['account']
    tagKey = event['detail']['resourcesAffected']['s3Object']['tags'][0]['key'] 
    tagValue = event['detail']['resourcesAffected']['s3Object']['tags'][0]['value'] 
    encryptionTypeFile = event['detail']['resourcesAffected']['s3Object']['serverSideEncryption']['encryptionType'] 
    encryptionTypeBucket = event['detail']['resourcesAffected']['s3Bucket']['defaultServerSideEncryption']['encryptionType']
    bkN = event['detail']['resourcesAffected']['s3Bucket']['name']
    feN = event['detail']['resourcesAffected']['s3Object']['key']
    dataIdentifiersTriggered = event['detail']['classificationDetails']['result']['customDataIdentifiers']['detections'][0]['name']
    
    sbT = "Sensitive Data has been discoved in a bucket that is not correctly tagged or classified."
    msT = "Sensitive Data has been discoved in a bucket that belongs to "+accountId+" that is not correctly tagged or classified.\n\nThis has been remediated automatically:\n\n"
    msT = msT + 'The filename is: '+feN+'\n'
    msT = msT + 'It was located in bucket: '+bkN+'\n'
    msT = msT + 'It was found by '+dataIdentifiersTriggered+'\n'
    msT = msT + 'This means it contains sensitive project data and must be protected.\n\n'
    msT = msT + 'This is out of compliance with our data protection standards\n'
    msT = msT + '- The '+tagKey+' tag is '+tagValue+' and it should be '+stV+'\n'
    msT = msT + '- The bucket encryption is '+encryptionTypeBucket+' and it needs to be AWS:KMS\n'
    msT = msT + '- The file encryption is '+encryptionTypeFile+' and it needs to be AWS:KMS\n'
    msT = msT + 'The file has been moved to '+secureBucket+'\n'

    #copy the object to the secure holding bucket
    copySource = { 'Bucket': bkN, 'Key':feN }
    try:
        response = s3c.copy(copySource, secureBucket, feN)
        response = s3c.delete_object(Bucket=bkN,Key=feN)
        response = s3c.put_object_tagging(Bucket=secureBucket,Key=feN,Tagging={'TagSet': [{'Key':'Classification','Value':stV},]})    

        tmpFn = '/tmp/'+getRandom(20)
        f = open(tmpFn, 'w')
        f.write("Moved to s3://"+secureBucket+"/"+feN)
        f.close
        with open(tmpFn, 'rb') as f:
            response = s3c.upload_fileobj(f, bkN, feN)
    except Exception as e:
        print(e)
    # Notify the administrator
    response = snsc.publish(
        TopicArn=snsTopicArn,
        Message=msT,
        Subject=sbT
        )

    return {
        'statusCode': 200,
    }    
