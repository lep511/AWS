import os
import time
import boto3
from amazondax import AmazonDaxClient
from boto3 import client, resource
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from random import randint
from datetime import date

db_source = os.environ.get("db_source")
print(db_source)

if (db_source != None and "dax" in db_source):
    client = AmazonDaxClient(endpoint_url=db_source)
    resource = AmazonDaxClient.resource(endpoint_url=db_source)
else:
    client = client(db_source)
    resource = resource(db_source)

acctTable = resource.Table('accounts')
transTable = resource.Table('transactions')
userTable = resource.Table('users')

def userLogin(username):

    response = userTable.get_item(
        Key = 
           { 'id'      : username
        },
        AttributesToGet=[
            'id', 'name' , 'user_type', 'password'
        ]
    )
    return response

def addTransactions(id, title, author):

    response = transTable.put_item(
        Item = {
            'id'     : id,
            'title'  : title,
            'author' : author,
            'likes'  : 0
        }
    )

    return response


def getAccountDetailsByAcctId(acc_id):

    response = acctTable.query(TableName='accounts',
            KeyConditionExpression=Key('acc_id').eq(acc_id)
    )
    
    return response



def getAccountDetailsByCustId(cust_id):
        
    response = client.query( 
        TableName='accounts',
        IndexName='cust_id_index',
        KeyConditionExpression='cust_id = :cust_id',
        ExpressionAttributeValues={
                ':cust_id': {'N': cust_id}
            }
    )
    deserializer = TypeDeserializer() 
    data = []
    for i in response['Items']:
        deserialized_document = {k: deserializer.deserialize(v) for k, v in i.items()}
        print(deserialized_document)
        data.append(deserialized_document)
        print(data)
    
    return data


def updateAcctBalance(acc_id, balance):
    response = acctTable.update_item(
        Key = {
            'acc_id': acc_id
        },
        AttributeUpdates={
            'balance': {
                'Value'  : balance,
                'Action' : 'PUT' # # available options -> DELETE(delete), PUT(set), ADD(increment)
            }
        },
        ReturnValues = "UPDATED_NEW"  # returns the new updated values
    )
    return response

def insertTransactions(acc_id,trans_message,amount):   
    resource1 = boto3.resource("dynamodb")
    tTable = resource1.Table('transactions')
    response = tTable.put_item(Item = {"trans_id": randint(0,10000), "acc_id": int(acc_id), "trans_message": trans_message, "last_updated_date": str(date.today()), "amount" : int(amount)})   
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
        return {
            'msg': 'Add transaction successful',
        }
    return { 
        'msg': 'error occurred',
        'response': response
    }

def getTransactions(acc_id,number):
    response = transTable.query( TableName='transactions',
            KeyConditionExpression=Key('acc_id').eq(acc_id),
            Limit=int(number),
            ScanIndexForward=True)

    return response
    

def transactionUpdate(src_data,trg_data,src_balance,trg_balance,amount):
    response = client.transact_write_items(
                TransactItems=[
                    {
                        'Update': {
                            'TableName': 'accounts',
                            'Key': {
                                'acc_id': {'N': str(trg_data['acc_id'])},
                            },
                            'ExpressionAttributeNames': {
                                '#balance': "balance"
                            },
                            'ExpressionAttributeValues': {
                                ':balance': {'N': str(trg_balance)},
                            },
                            'UpdateExpression': "SET #balance = :balance" 
                        }
                    },
                    {
                        'Put': {
                            'TableName': 'transactions',
                            'Item': {
                                'trans_id': {'N': str(randint(0,10000))},
                                'acc_id': {'N': str(trg_data['acc_id'])},
                                'last_updated_date': {'S': str(date.today())},
                                'amount': {'N': str(amount)},
                                'trans_message': {'S': str("Amount transferred")}

                            }
                        }
                    },
                    {                                            
                        'Update': {
                            'TableName': 'accounts',
                            'Key': {
                                'acc_id': {'N': str(src_data['acc_id'])},
                            },
                            'ExpressionAttributeNames': {
                                '#balance': "balance"
                            },
                            'ExpressionAttributeValues': {
                                ':balance': {'N': str(src_balance)},
                            },
                            'UpdateExpression': "SET #balance = :balance" 
                        }
                    },
                    {
                        'Put': {
                            'TableName': 'transactions',
                            'Item': {
                                'trans_id': {'N': str(randint(0,10000))},
                                'acc_id': {'N': str(src_data['acc_id'])},
                                'last_updated_date': {'S': str(date.today())},
                                'amount': {'N': str(amount)},
                                'trans_message': {'S': str("Amount transferred")}

                            }
                        }
                    }
                ]
    )
    return response
