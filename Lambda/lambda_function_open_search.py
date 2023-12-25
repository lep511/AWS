'''
search:
GET http://api_url/r4/Patient
GET http://api_url/r4/Patient?birthdate=2001-01-19
------------------------------------------------------------
read:
GET http://api_url/r4/Patient/1

create:
POST http://api_url/r4/Patient

update:
PUT http://api_url/r4/Patient/1

delete:
DELETE http://api_url/r4/Patient/1
'''
import boto3
import json
import base64
import requests
from requests_aws4auth import AWS4Auth
from datetime import datetime
import uuid
from datetime import datetime
import os

service = 'es'
credentials = boto3.Session().get_credentials()
session = boto3.session.Session()
region = session.region_name
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = os.environ['host']
index = os.environ['index']
api_url = os.environ['api_url']

headers = { "Content-Type": "application/json" }

dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')
table = dynamo_resource.Table("fhir-resource")

def lambda_handler(event, context):
    # current dateTime
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    operation = event['httpMethod']
    payload = {}
    response = 'ok'

    #read / search
    if operation == 'GET':
        response = get(event, date_time_str, payload)

    #create    
    elif operation == 'POST':
        response = post(event, date_time_str, payload)
        
    #update    
    elif operation == 'PUT':
        response = put(event, date_time_str, payload)
        
    #delete    
    elif operation == 'DELETE':
        response = delete(event, date_time_str, payload)

    return respond(None, response)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    
def get(event, date_time_str, payload):
    #search
    if event['queryStringParameters'] != None:
        queryStringParameters = event['queryStringParameters']
        param_docs = []
        for param in queryStringParameters:
            key = param.replace('r4', '').replace('Patient', '').replace('patient', '').replace('/', '').replace('?', '')
            value = queryStringParameters[param]
            param_doc = {
              "match": {
                key: value
              }
            }
            param_docs.append(param_doc)
            
        query_doc = {
          "query": {
            "bool": {
              "must": param_docs
            }
          }
        }
    
        url = host + '/' + index + '/' + '_search'
        responsedata = requests.get(url, auth=awsauth, json=query_doc, headers=headers)
        json_object = json.loads(responsedata.text)
        hits = json_object['hits']['total']['value']
        entries = []
        
        if hits == 0:
            responsedata = {
              "resourceType": "Bundle",
              "id": str(uuid.uuid4()),
              "meta": {
                "lastUpdated": date_time_str
              },
              "type": "searchset",
              "total": 0,
              "link": [ {
                "relation": "self",
                "url": "{}{}".format(api_url, event['path'])
              } ]
            }
            print('returning hits 0')
            return responsedata
        elif hits == 1:
            responsedata = json_object['hits']['hits'][0]['_source']
            print('returning hits 1')
            return responsedata
        elif hits > 1:
            for hit in json_object['hits']['hits']:
                entries.append(hit['_source'])
    
            entries_doc = {
              "resourceType": "Bundle",
              "id": str(uuid.uuid4()),
              "meta": {
                "lastUpdated": date_time_str
              },
              "type": "searchset",
              "link": [ {
                "relation": "self",
                "url": "{}{}".format(api_url, event['path'])
              }],
              "entry": entries
            }
            
            responsedata = entries_doc
            print('returning hits >1')
            return responsedata
            
    #read
    elif event['pathParameters'] != None:
        path = event['pathParameters']['proxy'].lower()
        print('returning read 0')
        if 'patient' in path:
            print('returning read 1')
            path_list = path.split("/")
            my_id = path_list.pop()
            my_key = {"id":my_id}
            ddb_response = table.get_item(Key=my_key)
            responsedata = ddb_response["Item"]
            print('returning read 2')
            return responsedata
            
def post(event, date_time_str, payload):
    payload = json.loads(event['body'])
    table.put_item(Item=payload)
    responsedata = payload
    return responsedata
    
def put(event, date_time_str, payload):
    payload = json.loads(event['body'])
    table.put_item(Item=payload)
    responsedata = payload
    return responsedata
    
def delete(event, date_time_str, payload):
    if event['pathParameters'] != None:
        path = event['pathParameters']['proxy'].lower()
        if 'patient' in path:
            path_list = path.split("/")
            my_id = path_list.pop()
            my_key = {"id":my_id}
            ddb_response = table.delete_item(Key=my_key)
            responsedata = "SUCCESSFUL_DELETE"
            return responsedata