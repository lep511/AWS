import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from spdynamodb.models import handle_error
import json
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import re

class DecimalEncoder_(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def query_main(table, pk_value, sk_value=None, index_name=None, consistent_read=False, consumed_capacity=None):
    """
    Gets item data from the table.
    :param table: The table object.
    :param pk_value: Primary key value.
    :param sk_value: Sort key value if exist. Default: None.
    :param index_name: The name of the index to query. Default: None.
    :param consistent_read: If True, then a strongly consistent read is used.
    :param consumed_capacity: Return the consumed capacity. Valid values: None, "TOTAL", "INDEXES". Default: None.
    :return: The data about the requested item.
    """
    if consumed_capacity is None or False: consumed_capacity = 'NONE'
    if consumed_capacity is True: consumed_capacity = 'TOTAL'
    pk_name = table.key_schema[0]['AttributeName']
    pk_type = table.attribute_definitions[0]["AttributeType"]
    map_type = {'S': str, 'N': int, 'B': bytes}
    index_exist = False
    sk_name = None
    
    
    if index_name:
        if table.global_secondary_indexes:
            all_index = [index['IndexName'] for index in table.global_secondary_indexes]
        else:
            handle_error(f"The table does not have any indexes.")
            return

        if index_name not in all_index:
            handle_error(f"The index name is incorrect. The table has the following indexes {all_index}")
            return
        else:
            index_exist = True
            index_data = [index for index in table.global_secondary_indexes if index['IndexName'] == index_name][0]
            pk_name = index_data['KeySchema'][0]['AttributeName']
            pk_type = [m for m in table.attribute_definitions if m['AttributeName'] == pk_name][0]['AttributeType']
            try:
                sk_name = index_data['KeySchema'][1]['AttributeName']
            except:
                sk_name = False
    else:
        try:
            sk_name = table.key_schema[1]['AttributeName']
        except:
            sk_name = None
                
    if type(pk_value) != map_type[pk_type]:
        handle_error(f"The format of the main key is incorrect, it should be: {pk_type}")
        return
        
    if not sk_name:
        # If the sort key does not exist only run get_item
        response = table.get_item(
            Key={pk_name: pk_value},
            ConsistentRead=consistent_read,
            ReturnConsumedCapacity=consumed_capacity
        )

    else:
        # If the sort key exists
 
        if sk_value is None:
            handle_error(f"The sort key value cannot be empty.")
            return
 
        elif isinstance(sk_value, (int, float)):
            sk_value = Decimal(str(sk_value))
            qry = False
        
        elif sk_value.startswith("<="):
            value = Decimal(sk_value[2:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).lte(value)

        elif sk_value.startswith("<"):
            value = Decimal(sk_value[1:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).lt(value)

        elif sk_value.startswith("=="):
            value = Decimal(sk_value[2:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).eq(value)
  
        elif sk_value.startswith(">="):
            value = Decimal(sk_value[2:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).gte(value)
  
        elif sk_value.startswith(">"):
            value = Decimal(sk_value[1:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).gt(value)
  
        elif sk_value.startswith("!="):
            value = Decimal(sk_value[2:])
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).ne(value)
   
        elif sk_value.endswith("*"):
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).begins_with(sk_value[:-1])
            
        elif re.search(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$', sk_value):
            value = sk_value.split("_")
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).between(*value)
 
        elif re.search(r'\d+_\d+', sk_value):
            value = sk_value.split("_")
            value_dec = [Decimal(x) for x in value]
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).between(*value_dec)
        elif "_" in sk_value:
            value = sk_value.split("_")
            qry = Key(pk_name).eq(pk_value) & Key(sk_name).between(*value)
   
        else:
            qry = False

        
        if qry:
            if index_exist:
                try:
                    response = table.query(
                        IndexName=index_name,
                        KeyConditionExpression=qry,
                        ConsistentRead=consistent_read,
                        ReturnConsumedCapacity=consumed_capacity
                    )
                except ClientError as error:
                    handle_error(error)
                    return
                except BaseException as error:
                    print("Unknown error while getting item: " + error.response['Error']['Message'])
                    return
            else:
                try:
                    response = table.query(
                        KeyConditionExpression=qry,
                        ConsistentRead=consistent_read,
                        ReturnConsumedCapacity=consumed_capacity
                    )
                except ClientError as error:
                    handle_error(error)
                    return
                except BaseException as error:
                    print("Unknown error while getting item: " + error.response['Error']['Message'])
                    return
        else:
            if not index_exist:
                try:
                    response = table.get_item(
                        Key={pk_name: pk_value, sk_name: sk_value},
                        ConsistentRead=consistent_read,
                        ReturnConsumedCapacity=consumed_capacity
                    )
                except ClientError as error:
                    handle_error(error)
                    return
                except BaseException as error:
                    print("Unknown error while getting item: " + error.response['Error']['Message'])
                    return
                    
            else:
                try:
                    response = table.query(
                        IndexName=index_name,
                        KeyConditionExpression=Key(pk_name).eq(pk_value) & Key(sk_name).eq(sk_value),
                        ConsistentRead=consistent_read,
                        ReturnConsumedCapacity=consumed_capacity
                    )
                except ClientError as error:
                    handle_error(error)
                    return
                except BaseException as error:
                    print("Unknown error while getting item: " + error.response['Error']['Message'])
                    return
                    
    if response.get('Item'):
        js_data = json.dumps(response['Item'], cls=DecimalEncoder_)
        result = json.loads(js_data)
    elif response.get('Items'):
        js_data = json.dumps(response['Items'], cls=DecimalEncoder_)
        result = json.loads(js_data)
    else:
        print(f"Item not found: {pk_value} - {sk_value}")
        result = None
        
    if consumed_capacity != 'NONE':
        response_json = json.loads(json.dumps(response['ConsumedCapacity'], cls=DecimalEncoder_))
        consumed_capacity_count = response_json['CapacityUnits']
        print(f"Consumed Capacity: {consumed_capacity_count}")

    return result
   
    
def query_partiql_main(query, parameters=None, consumed_capacity=None, dyn_table=None):
    if consumed_capacity is None: consumed_capacity = 'NONE'
    if consumed_capacity == True: consumed_capacity = 'TOTAL'
    
    try:
        response = dyn_table.meta.client.execute_statement(Statement=query, ReturnConsumedCapacity=consumed_capacity)
        print("ExecuteStatement executed successfully.")
    except ClientError as error:
        handle_error(error)
        return
    
    except BaseException as error:
        print("Unknown error while executing executeStatement operation: " + error.response['Error']['Message'])
        return
    
    if consumed_capacity != 'NONE':
        response_json = json.loads(json.dumps(response['ConsumedCapacity'], cls=DecimalEncoder_))
        consumed_capacity_count = response_json['CapacityUnits']
        print(f"Consumed Capacity: {consumed_capacity_count}")
        
    if len(response.get('Items')) == 0:
        print("Not found any items")
        return None
    
    json_data = json.loads(json.dumps(response['Items'], cls=DecimalEncoder_))
    
    return json_data