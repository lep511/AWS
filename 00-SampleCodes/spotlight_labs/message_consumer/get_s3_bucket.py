import boto3

s3 = boto3.client('s3')
tagging = boto3.client('resourcegroupstaggingapi') 

s3bucketwithtags = tagging.get_resources(TagFilters=[{'Key': 'Project','Values':['Spotlight']}],ResourceTypeFilters=['s3']) 
s3_bucket_arn = s3bucketwithtags['ResourceTagMappingList'][0]['ResourceARN']
s3_bucket = s3_bucket_arn.split(':::')[1]
print(s3_bucket)
