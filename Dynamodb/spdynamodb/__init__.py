#import awswrangler as wr 
from awswrangler import dynamodb as wr_d
from decimal import Decimal
from io import BytesIO
from datetime import datetime
import ast
import json
import gzip
import logging
import os
import boto3
import pandas as pd
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, TypeVar, Union, cast
from boto3.dynamodb.types import Binary
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)

__version__ = "1.2.0"

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class DynamoTable:
    min_compress = 250
    
    def __init__(self, table_name=None, profile_name=None, region='us-east-1'):
        """
        :param table_name: A DynamoDB table.
        """
        self.table_name = table_name
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.dyn_resource = self.session.resource("dynamodb", region_name=region)
        self.region = region
        self.__keyType = {"S": "s", "N": 0, "B": b"b"}
        if not table_name:
            self.table_name = None
        elif not self.exists(table_name):
            logger.error(
                "Table %s doesn't exist. To create use create_table() function.",
                table_name)
            self.table_name = None
            raise
        else:
            self.select_table(table_name)
        
    def __repr__(self):
        if self.table_name != None:
            self.table.reload()
            rep = f"- Table name: {self.table_name}\
            \n- Table arn: {self.table.table_arn}\
            \n- Table creation: {self.table.creation_date_time}\
            \n- {self.table.key_schema}\
            \n- {self.table.attribute_definitions}"
        else:
            rep = "The table has not yet been selected"
        return rep
    
    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.
        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            self.table = self.dyn_resource.Table(table_name)
            self.table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        return exists
    
    def select_table(self, table_name):
        if not self.exists(table_name):
            self.table_name = None
            raise ValueError("Table doesn't exist. To create use create_table() function.")
        else:
            self.table_name = table_name
            if self.table.billing_mode_summary:
                self.bill_mode = self.table.billing_mode_summary['BillingMode']
            else:
                self.bill_mode = 'PROVISIONED'
            
    @property
    def all_tables(self):
        """
        Returns all tables in a region
        """
        response = {"Region": self.region}
        response["Tables"] = list(self.dyn_resource.tables.all())
        return response

    
    def create_table(self, 
                     table_name, 
                     partition_key, 
                     partition_key_type, 
                     sort_key=None, 
                     sort_key_type=None,
                     provisioned=True, # or 'PAY_PER_REQUEST'
                     rcu=5, 
                     wcu=5
                    ):
        """
        Creates an Amazon DynamoDB table.
        :param table_name: The name of the table to create.
        :param partition_key: Primary key name.
        :param partition_key_type: Primary key type.
        :param sort_key: Sort key name. Default: None.
        :param sort_key_type: Sort key type. Default: None.
        :param provisioned: True = PROVISIONED, False = PAY_PER_REQUEST. Default: True.
        :param rcu: (Read Capacity Units) Default: 10. The maximum number of strongly consistent reads 
                    consumed per second before DynamoDB returns a ThrottlingException. Default: 5.
        :param wcu: (WriteCapacityUnits) Default: 10. The maximum number of writes consumed per second 
                    before DynamoDB returns a ThrottlingException. Default: 5.
        """           
        
        key_schema = [{'AttributeName': partition_key, 'KeyType': 'HASH'}]
        att_definition=[{'AttributeName': partition_key, 'AttributeType': partition_key_type}]
              
        if sort_key != None:
            key_schema.append({'AttributeName': sort_key, 'KeyType': 'RANGE'})
            att_definition.append({'AttributeName': sort_key, 'AttributeType': sort_key_type})

        try:
            if provisioned:
                self.bill_mode = 'PROVISIONED'
                self.table = self.dyn_resource.create_table(
                    TableName=table_name, 
                    KeySchema = key_schema, 
                    AttributeDefinitions = att_definition,
                    ProvisionedThroughput={'ReadCapacityUnits': rcu,
                                           'WriteCapacityUnits': wcu
                                          }
                )
            else:
                self.bill_mode = 'PAY_PER_REQUEST'
                self.table = self.dyn_resource.create_table(
                    TableName=table_name, 
                    KeySchema = key_schema, 
                    AttributeDefinitions = att_definition,
                    BillingMode="PAY_PER_REQUEST")
            self.table.wait_until_exists()
            self.table_name = table_name
            logger.info("Table created successfully!")

        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
    
    def batch_pandas(self, dataframe, compress=False):
        json_df = dataframe.fillna("").to_json(orient="records")
        parsed = json.loads(json_df, parse_float=Decimal)
        if compress:
            parsed = self.convert_binary(parsed)      
        self.write_batch(parsed)
        
    def load_json(self, json_file, compress=False):
        try:
            with open(json_file) as json_data:
                parsed = json.load(json_data, parse_float=Decimal)
        except:
            logger.error(
                "Couldn't load data from %s or the file does not exist.", json_file)
            raise
        if compress:
            parsed = self.convert_binary(parsed)
        self.write_batch(parsed)
    
    def write_batch(self, items):
        """
        Fills an Amazon DynamoDB table with the specified data, using the Boto3
        Table.batch_writer() function to put the items in the table.
        Inside the context manager, Table.batch_writer builds a list of
        requests. On exiting the context manager, Table.batch_writer starts sending
        batches of write requests to Amazon DynamoDB and automatically
        handles chunking, buffering, and retrying.
        :param items: The data to put in the table. Each item must contain at least
                       the keys required by the schema that was specified when the
                       table was created.
        """
        try:
            with self.table.batch_writer() as writer:
                for item in items:
                    writer.put_item(Item=item)
        except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. Here's why: %s: %s", self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def add_item(self, item, compress=False):
        """
        Adds a item to the table.
        :param item: The item to add to the table.
        """
        if compress:
            for att in item:
                if type(att) == str:
                    if len(item[att]) > self.min_compress:
                        s_in = bytes(item[att], 'utf-8')
                        s_out = gzip.compress(s_in)
                        item[att] = s_out
        try:
            self.table.put_item(
                Item=item
            )
        except ClientError as err:
            logger.error(
                "Couldn't add item to table %s. Here's why: %s: %s",
                self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def get_item(self, pk_value, se_value=None):
        """
        Gets item data from the table.
        :param pk_value: Primary key value.
        :param se_value: Sort key value. Default: None.
        :return: The data about the requested item.
        """
        pk_name = self.table.key_schema[0]['AttributeName']
        pk_type = self.table.attribute_definitions[0]["AttributeType"]
        act_pk_type = self.__keyType[pk_type]
        
        if len(self.table.key_schema) == 2:
            sh_name = self.table.key_schema[1]['AttributeName']
            sh_type = self.table.attribute_definitions[1]["AttributeType"]
            act_sh_type = self.__keyType[sh_type]
            
            if se_value is None:
                logger.error(f"The sort key value cannot be empty: {sh_name}")
                return
            elif type(pk_value) != type(act_pk_type):
                logger.error(f"The format of the main key is incorrect, it should be: {type(act_pk_type)}")
                return
            elif type(se_value) != type(act_sh_type):
                logger.error(f"The format of the sort key is incorrect, it should be: {type(act_pk_type)}")
                return
            response = self.table.get_item(Key={pk_name: pk_value, sh_name: se_value})
        else:
            if type(pk_value) != type(act_pk_type):
                logger.info(f"The format of the main key is incorrect, it should be: {type(act_pk_type)}")
                return
            response = self.table.get_item(Key={pk_name: pk_value})
        try:
            #if self.found_binary(response):
                #response = self.decompress_binary(response)
            js_data = json.dumps(response['Item'], cls=DecimalEncoder)
            result = json.loads(js_data)
            return result
        except:
            return response

    def scan_att(self, att_name, query, to_pandas=True, consumed_capacity=False, pages=None):
        scan_kwargs = {
            'FilterExpression': Attr(att_name).eq(query),
            'ReturnConsumedCapacity': "TOTAL"
        }
        done = False
        start_key = None
        response_total = []
        response_final = []
        consumed_capacity_count = 0
        if pages is None:
            pages = 1000
        
        while not done and pages != 0:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            response = self.table.scan(**scan_kwargs)
            response_total.append(response['Items'])
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
            consumed_capacity_count += response['ConsumedCapacity']['CapacityUnits']   
            pages -= 1

        if consumed_capacity:
            logger.info(f"Consumed Capacity: {consumed_capacity_count}")
        
        for elem in response_total:
            for item in elem:
                response_final.append(item)
        
        if to_pandas:
            return pd.DataFrame(response_final)
        else:
            return response_final
        
    def update_item(self, title, year, rating, plot):
        """
        Updates rating and plot data for a movie in the table.
        :param title: The title of the movie to update.
        :param year: The release year of the movie to update.
        :param rating: The updated rating to the give the movie.
        :param plot: The updated plot summary to give the movie.
        :return: The fields that were updated, with their new values.
        """
        try:
            response = self.table.update_item(
                Key={'year': year, 'title': title},
                UpdateExpression="set info.rating=:r, info.plot=:p",
                ExpressionAttributeValues={
                    ':r': Decimal(str(rating)), ':p': plot},
                ReturnValues="UPDATED_NEW")
        except ClientError as err:
            logger.error(
                "Couldn't update movie %s in table %s. Here's why: %s: %s",
                title, self.table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Attributes']

    def query_partiql(self, query: str, parameters: Optional[List[Any]] = None, chunked: bool = False):
        if "<table>" in query:
            query = query.replace("<table>", self.table.name)
        resp = wr_d.read_partiql_query(query=query, parameters=parameters, chunked=chunked, boto3_session=self.session)
        return resp
                      
    def query_items(self, query, index_name=None, to_pandas=False, consumed_capacity=False):
        """
        Query a table items.
        :param query: The key value to query.
        :param index_name: The index name to query. Default: None.
        :param to_pandas: If True, returns a pandas DataFrame. Default: False.
        :param consumed_capacity: If True, returns the consumed capacity. Default: False.
        :return: Items matching the search.
        """
        try:
            # If an index was specified, query the index
            if index_name:
                response = self.table.query(
                        IndexName=index_name, 
                        KeyConditionExpression=Key('Language_code').eq(query)
                )
                consumed_capacity = False # Indexes don't have consumed capacity
            # If no index was specified, query the table
            else:          
                pk_name = self.table.key_schema[0]['AttributeName']
                response = self.table.query(
                        KeyConditionExpression=Key(pk_name).eq(query), 
                        ReturnConsumedCapacity="TOTAL"
                )
        except ClientError as err:
            logger.error(
                f"Couldn't query for {query}. Here's why: {err.response['Error']['Code']} \
                {err.response['Error']['Message']}")
            raise
        
        if consumed_capacity:
            consumed_text = f"Consumed Capacity: {response['ConsumedCapacity']['CapacityUnits']}"
            logger.info(consumed_text)
        
        if len(response['Items']) == 0:
            logger.info("No items were found matching your search query.")
            return None
        
        if self.found_binary(response, only_check=True):
            response = self.decompress_binary(response)
        
        if to_pandas:
            return pd.DataFrame(response['Items'])
        else:
            return response['Items']


    def create_global_secondary_index(self, att_name, att_type, i_name=None, sort_index=None, 
                                      sort_type=None, proj_type="ALL", i_rcu=5, i_wcu=5):
        """
        Add a global secondary index to a DynamoDB table
        :param att_name: Name of attribute.
        :param att_type: Attribute type (S-String, N-Number, B-Binary).
        :param sort_index: Name of sort index. Default: None
        :param sort_type: Attribute type (S-String, N-Number, B-Binary). Default: None
        :param i_name: Name of index. Default: <att_name>-index
        :param proj_type: Represents attributes that are copied (projected) from the table into the global secondary index
                          (ALL, KEYS_ONLY, [list of INCLUDE non-key attribute])
        :param i_rcu: Read capacity units. Default: 5
        :param i_wcu: Write capacity units. Default: 5
        """
        # Check index name
        if not i_name:
            i_name = att_name + "-index"
        
        # Check parameter proj_type
        if type(proj_type) == list:
            project = {
                "ProjectionType": "INCLUDE",
                "NonKeyAttributes": proj_type
            }
        else:
            project = {
                "ProjectionType": proj_type,
            }
        # Check parameter sort_index and sort_type
        if sort_index != None:
            key_schema = [
                        {'AttributeName': att_name, 'KeyType': 'HASH'},  
                        {'AttributeName': sort_index, 'KeyType': 'RANGE'}]
            att_definition = [
                        {'AttributeName': att_name, 'AttributeType': att_type},
                        {'AttributeName': sort_index, 'AttributeType': sort_type}]
        else:
            key_schema = [{'AttributeName': att_name, 'KeyType': 'HASH'}]
            att_definition=[{'AttributeName': att_name, 'AttributeType': att_type}]
        ### Main Parameter
        gsi_main =  [
                        {
                            "Create": {
                                "IndexName": i_name,
                                "KeySchema": key_schema,
                                "Projection": project
                                # Global secondary indexes have read and write capacity separate from the underlying table.
                            }
                        }
        ]
        # Global secondary indexes have read and write capacity separate from the underlying table.
        # If not selected PAY_PER_REQUEST when create table
        if self.bill_mode == "PROVISIONED":
            provisiones_thro = {
                                "ReadCapacityUnits": i_rcu,
                                "WriteCapacityUnits": i_wcu
            }
            gsi_main[0]['Create']['ProvisionedThroughput'] = provisiones_thro
        
        try:
            self.client = self.session.client('dynamodb', region_name=self.region)
            resp = self.client.update_table(
                TableName = self.table_name,
                AttributeDefinitions=att_definition,
                GlobalSecondaryIndexUpdates=gsi_main
            )
            self.table.reload()
        except ClientError as err:
            logger.error(
                "Global secondary index could not be created in table %s. Here's why: %s: %s",
                self.table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def check_status_gsi(self, index_name=None):
        """
        Usually, a new GSI should be created within 5 minutes. But the time duration can increase 
        when adding a GSI to an existing table since DynamoDB needs to backfill all the existing 
        database records.
        :param name_gsi: The name of global secondary index.
        """
        self.table.reload()
        list_names = []
        actual_status = []
        status = None
        if self.table.global_secondary_indexes:
            for i in self.table.global_secondary_indexes:
                if index_name == i['IndexName']: 
                    return i['IndexStatus']
                list_names.append(i['IndexName'])
                actual_status.append(i['IndexStatus'])
        
            if 'CREATING' in actual_status:
                status = 'CREATING'
            elif 'UPDATING' in actual_status:
                status = 'UPDATING'
            elif 'DELETING' in actual_status:
                status = 'DELETING'
            else:
                status = 'ACTIVE'
        
        if index_name: raise ValueError("Global secondary index does not exist.")       
        
        return status
            
    @property
    def list_gsi(self):
        """
        Returns a list of all global secondary indexes of the table.
        """
        if self.table.global_secondary_indexes:
            all_gsi = []
            for gsi_name in self.table.global_secondary_indexes:
                all_gsi.append(gsi_name["IndexName"])
            return all_gsi
        else:
            return None
    
    def found_binary(self, response, only_check=False):
        bin_found = []
        elem = "Item" if "Item" in response else "Items"
        
        if elem == "Item":
            for att in response[elem]:
                if type(response[elem][att]) is Binary:
                    bin_found.append(att)
                    if only_check: return True
        
        else:
            for i in range(len(response[elem])):
                for att in response[elem][i]:
                    if type(response[elem][i][att]) is Binary:
                        bin_found.append(att)
                        if only_check: return True
                    
        if len(bin_found) != 0:
            return bin_found
        else:
            return False
        
    def check_binary(self, item):
        if type(item) == str:
            if len(item) > self.min_compress:
                return True
        return False
    
    def convert_binary(self, parsed):
        for i in range(len(parsed)):
            for key, value in parsed[i].items():
                if self.check_binary(value):
                    s_in = bytes(value, 'utf-8')
                    s_out = gzip.compress(s_in)
                    parsed[i][key] = s_out
        return parsed
    
    def decompress_binary(self, response):
        elem = "Item" if "Item" in response else "Items"
        
        if elem == "Item":
            binary_att = self.found_binary(response)
            for att in binary_att:
                try:
                    val_att = response[elem][att].value
                    val_dec = gzip.decompress(val_att).decode()
                    response[elem][att] = val_dec
                except:
                    pass
        else:
            for i in range(len(response[elem])):
                for att in response[elem][i]:
                    if type(response[elem][i][att]) is Binary:
                        val_att = response[elem][i][att].value
                        val_dec = gzip.decompress(val_att).decode()
                        response[elem][i][att] = val_dec
            
        return response