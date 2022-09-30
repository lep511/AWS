import json, urllib, boto3, time
import os, sys, logging
from hashlib import blake2b

logger = logging.getLogger()
logger.setLevel(logging.INFO)

runtimeRegion = os.environ['AWS_REGION']
dynamodb = boto3.resource('dynamodb', region_name=runtimeRegion)
s3 = boto3.client('s3', region_name=runtimeRegion)

# This handler is executed every time the Lambda function is triggered
def lambda_handler(event, context):
  # Show the incoming event in the debug log
  print("Event received by Lambda function: " + json.dumps(event, indent=2))

  imageMetadataTableName = os.environ['imageMetadataTableName']
  imageMetadataTable = dynamodb.Table(imageMetadataTableName)
  s3BucketName = os.environ['s3BucketName']
  # Read and convert the event variable to a useable format
  body = json.loads(event['body'])
  # Save information from body to common name variables of the correct type
  userName = str(body['userName'])
  albumName = str(body['albumName'])
  message = str(body['message'])
  numberOfImages = int(body['numberOfImages'])

  # Create an output variable to store the information to return
  output = {'userName':  userName,
            'albumName': albumName,
            'message':   message,
            'numberOfImages': numberOfImages}

  # Put a limit on number of presigned URL's
  if (numberOfImages > 10):
    numberOfImages = 10

  # Iterate through the number of items generated presigned Urls and inserting the information into DynamoDB
  count = 0
  while (count < numberOfImages):
    # Create file name
    uid = userName+'/'+albumName+'/' + userName + '_' + albumName + '_' + str(count) + '.jpg'
    #Replace white spaces with underscore
    uid = uid.replace(" ", "_")
    fileName = 'Incoming/'+ uid

    # get presigned url, valid for 900sec (5min)
    presignedUrl = s3.generate_presigned_url('put_object', Params={'Bucket':s3BucketName, 'Key':fileName}, ExpiresIn=900, HttpMethod='PUT')
    logger.info(fileName + " : " + presignedUrl)
    presignedUrl = presignedUrl.split('.',4)
    presignedUrl = presignedUrl[0]+'.'+presignedUrl[1]+'-'+runtimeRegion+'.'+presignedUrl[2]+'.'+presignedUrl[3]+'.'+presignedUrl[4]
    logger.info(fileName + " : Region Endpoint : " + presignedUrl)

    output[count] = {
        'fileName': fileName,
        'bucket': s3BucketName,
        'presignUrl': presignedUrl
        }

    ts = time.time()
    timeStampBytes = bytes(str(ts), encoding="ascii")
    # Use the blake2b cryptographic hash function
    h = blake2b()
    h.update(timeStampBytes)
    h.hexdigest()

    #uid = albumName.replace(" ", "_") + '_' + str(count) + "_" + h.hexdigest()
    # insert image, album, user name, message, bucket, and presigned Url into table
    try:
      imageMetadataTable.put_item(
        Item={
          'imageID':      uid,
          'albumID':      albumName.replace(" ", "_"),
          'Album Name':   albumName,
          'User Name':    userName,
          'Message':      message,
          'File Name':    fileName,
          'Bucket':       s3BucketName,
          'PresignedUrl': presignedUrl
        })
    except Exception as e:
      logger.error("Unable to insert data into DynamoDB table"+format(e))
      logger.error(e)
    count += 1

  return {
    'statusCode': 200,
    'body': json.dumps(output)
  }
