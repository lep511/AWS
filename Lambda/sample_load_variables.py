import json, boto3, os, time

def handler(event, context):

  srcBucket= os.environ['BUCKET_NAME']
  # Read and convert the event variable to a useable format
  body = json.loads(event['body'])

  # Save information from body to common name variables of the correct type
  userName = body['userName']
  print('User name:', userName)
  albumName = body['albumName']
  print('Album name:', albumName)

  srcFolder = 'incoming/' + userName + '/' + albumName +'/'
  destFolder = 'Bookbind/' + userName + '/' + albumName + '/'

  print('Source Folder:', srcFolder)
  print('Desitnation Folder', destFolder)

  s3 = boto3.resource('s3')
  bucket = s3.Bucket(srcBucket)



  for obj in bucket.objects.filter(Prefix=srcFolder):
    old_source = {'Bucket': srcBucket, 'Key': obj.key}
    # replace the prefix
    new_key = obj.key.replace(srcFolder, destFolder, 1)
    new_obj = bucket.Object(new_key)
    new_obj.copy(old_source)
    time.sleep(5)

  return {
    'statusCode': 200,
    'body': json.dumps('Your book printing request has been received, once the digitla book is availble, you will recieve an email to validate the pdf book and a link to approve or reject the physical book printing.')
  }