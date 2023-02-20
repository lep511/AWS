from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import boto3
import json
import cfnresponse
def handler(event, context):
  print (str(event))
  responseData = {}
  contenttype = {'py':'text/x-python', 'png':'image/png', 'html': 'text/html', 'js': 'application/javascript', 'css': 'text/css', 'json':'application/json', 'zip':'application/zip', 'ico':'image/x-icon'}
  try: 
    SourceBucket = event['ResourceProperties']['SourceBucket']
    SourceKey = event['ResourceProperties']['SourceKey']
    DestinationBucket = event['ResourceProperties']['DestinationBucket']
    baseDir = '/tmp/' + DestinationBucket + '/'
    ZipDownload = '/tmp/'+SourceBucket+'.zip'
    print("SourceBucket=" + SourceBucket)
    print("SourceKey=" + SourceKey)
    print("DestinationBucket=" + DestinationBucket)
    print("baseDir=" + baseDir)
    print("ZipDownload=" + ZipDownload)
    s3client = boto3.client('s3')  
    s3client.download_file(SourceBucket, SourceKey, ZipDownload)
    print("downloaded")
    with ZipFile(ZipDownload) as zfile:
      zfile.extractall(baseDir)
    print("unzipped")
    for path, subdirs, files in os.walk(baseDir):
      for filename in files:
        print("filename=" + filename)
        extension = os.path.splitext(filename)[1][1:]
        print("extension=" + extension + ", content type=" + contenttype[extension] )
        f = os.path.join(path, filename)
        print("f=" + f)
        key = f.replace(baseDir, "", 1)
        print("key=" + key)
        s3client.upload_file(f, DestinationBucket, key, ExtraArgs={ 'ContentType': contenttype[extension] })
        print("uploaded")
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    print ('SUCCESS')
  except Exception as e:
    responseData['Error'] = str(e)
    cfnresponse.send(event, context, cfnresponse.FAILED, responseData) 
    print("FAILED ERROR: " + responseData['Error'])
