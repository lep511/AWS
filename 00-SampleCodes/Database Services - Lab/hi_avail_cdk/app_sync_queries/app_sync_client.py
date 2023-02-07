import json
import boto3
from appsyncclient import AppSyncClient

appsyncClient = AppSyncClient(region="us-east-1",apiId="p3s3ohg2sffu7mlh6pifr63bfa",apiKey="da2-a43kyjmdn5fnhozewxod6b3bvy",authenticationType="API_KEY")
query = json.dumps({"query": "{\n  all(limit:10) {\n    items{\n    name\n  items2Id\n}\n}\n}\n"})
response = appsyncClient.execute(data=query) 
print(json.dumps(response, indent=4, sort_keys=True))
