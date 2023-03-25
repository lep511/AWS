import pandas as pd
import json
import boto3
import random

print("Loading file...")
df = pd.read_csv("movies_compress.csv.gz", nrows=10000)
df = df.sort_values(by=['tconst']).reset_index().drop('Unnamed: 0', axis=1)
df = df.where(pd.notnull(df), None)
print("Load success!!")

kdsname='new-data-stream'
region='us-east-2'
i=0
clientkinesis = boto3.client('kinesis',region_name=region)

all_index = iter(range(len(df)))
iter_check = True

while iter_check == True:
   id_c = 'id' + str(random.randint(1665586, 8888888))
   n = 0
   list_data = []
   for i in all_index:
      data = df.iloc[i].to_json()
      list_data.append(data)
      if n > 100:
         break
      else:
         n += 1
       
   response=clientkinesis.put_record(StreamName=kdsname, Data=json.dumps(list_data), PartitionKey=id_c)
   print(str(i) + " - " + str(response['ResponseMetadata']['HTTPStatusCode']))
   print(response)
   iter_check = any(True for _ in all_index)
    
    
    