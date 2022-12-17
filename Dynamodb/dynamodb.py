from decimal import Decimal
from io import BytesIO
from datetime import datetime
import ast
import json
import gzip
import logging
import os
from pprint import pprint
import boto3
import pandas as pd
from boto3.dynamodb.types import Binary
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class DynamoTable:
    min_compress = 250
    
    def __init__(self, table_name=None, dyn_resource=None):
        """
        :param table_name: A DynamoDB table.
        """
        self.table_name = table_name
        if dyn_resource is None:
            self.dyn_resource = boto3.resource('dynamodb')
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
            rep = f"- Table name: {self.table_name}\
            \n- Table arn: {self.table.table_arn}\
            \n- Table creation: {self.table.creation_date_time}\
            \n- Billing mode: {self.table.billing_mode_summary['BillingMode']}\
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
            print("Table doesn't exist. To create use create_table() function.")
            self.table_name = None
        else:
            self.table_name = table_name

    @property
    def item_count(self):
        """
        Count items for a table
        """
        try:
            return self.table.item_count
        except:
            return 0
    
    def create_table(self, 
                     table_name, 
                     partition_key, 
                     partition_key_type, 
                     sort_key=None, 
                     sort_key_type=None, 
                     provisioned=False, # or 'PAY_PER_REQUEST'
                     rcu=10, 
                     wcu=10
                    ):
        """
        Creates an Amazon DynamoDB table.
        :param table_name: The name of the table to create.
        :param partition_key: Primary key name.
        :param partition_key_type: Primary key type.
        :param sort_key: Sort key name.
        :param sort_key_type: Sort key type.
        :param rcu: (Read Capacity Units) Default: 10. The maximum number of strongly consistent reads 
                    consumed per second before DynamoDB returns a ThrottlingException.
        :param wcu: (WriteCapacityUnits) Default: 10. The maximum number of writes consumed per second 
                    before DynamoDB returns a ThrottlingException.
        """           
        if sort_key != None:
            key_schema = [
                        {'AttributeName': partition_key, 'KeyType': 'HASH'},  
                        {'AttributeName': sort_key, 'KeyType': 'RANGE'}]
            att_definition = [
                        {'AttributeName': partition_key, 'AttributeType': partition_key_type},
                        {'AttributeName': sort_key, 'AttributeType': sort_key_type}]
        else:
            key_schema = [{'AttributeName': partition_key, 'KeyType': 'HASH'}]
            att_definition=[{'AttributeName': partition_key, 'AttributeType': partition_key_type}]
        try:
            if provisioned:
                self.table = self.dyn_resource.create_table(
                    TableName=table_name, 
                    KeySchema = key_schema, 
                    AttributeDefinitions = att_definition,
                    ProvisionedThroughput={'ReadCapacityUnits': rcu,
                                           'WriteCapacityUnits': wcu
                                          }
                )
            else:
                self.table = self.dyn_resource.create_table(
                    TableName=table_name, 
                    KeySchema = key_schema, 
                    AttributeDefinitions = att_definition,
                    BillingMode="PAY_PER_REQUEST")
            self.table.wait_until_exists()
            self.table_name = table_name
            print("Table created successfully!")

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
        :param se_value: Sort key value.
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
                print(f"The sort key value cannot be empty: {sh_name}")
                return
            elif type(pk_value) != type(act_pk_type):
                print(f"The format of the main key is incorrect, it should be: {type(act_pk_type)}")
                return
            elif type(se_value) != type(act_sh_type):
                print(f"The format of the sort key is incorrect, it should be: {type(act_pk_type)}")
                return
            response = self.table.get_item(Key={pk_name: pk_value, sh_name: se_value})
        else:
            if type(pk_value) != type(act_pk_type):
                print(f"The format of the main key is incorrect, it should be: {type(act_pk_type)}")
                return
            response = self.table.get_item(Key={pk_name: pk_value})
        try:
            #if self.found_binary(response):
                #response = self.decompress_binary(response)
            js_data = json.dumps(response['Item'], cls=DecimalEncoder)
            result = json.loads(js_data)
            return result
        except:
            return (None, response)

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
            print(f"Consumed Capacity: {consumed_capacity_count}")
        
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
                title, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Attributes']

    def query_items(self, query, to_pandas=False, consumed_capacity=False):
        """
        Query a table items.
        :param query: The key value to query.
        :return: Items matching the search.
        """
        try:
            pk_name = self.table.key_schema[0]['AttributeName']
            response = self.table.query(KeyConditionExpression=Key(pk_name).eq(query), 
                                        ReturnConsumedCapacity="TOTAL"
            )
        except ClientError as err:
            logger.error(
                f"Couldn't query for {query}. Here's why: {err.response['Error']['Code']} \
                {err.response['Error']['Message']}")
            raise
        
        if consumed_capacity:
            consumed_text = f"Consumed Capacity: {response['ConsumedCapacity']['CapacityUnits']}"
            print(consumed_text)
        
        if len(response['Items']) == 0:
            print("No items were found matching your search query.")
            return None
        
        if self.found_binary(response, only_check=True):
            response = self.decompress_binary(response)
        
        if to_pandas:
            return pd.DataFrame(response['Items'])
        else:
            return response['Items']


    def scan_movies(self, year_range):
        """
        Scans for movies that were released in a range of years.
        Uses a projection expression to return a subset of data for each movie.
        :param year_range: The range of years to retrieve.
        :return: The list of movies released in the specified years.
        """
        movies = []
        scan_kwargs = {
            'FilterExpression': Key('year').between(year_range['first'], year_range['second']),
            'ProjectionExpression': "#yr, title, info.rating",
            'ExpressionAttributeNames': {"#yr": "year"}}
        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                response = self.table.scan(**scan_kwargs)
                movies.extend(response.get('Items', []))
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as err:
            logger.error(
                "Couldn't scan for movies. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

        return movies

    def delete_movie(self, title, year):
        """
        Deletes a movie from the table.
        :param title: The title of the movie to delete.
        :param year: The release year of the movie to delete.
        """
        try:
            self.table.delete_item(Key={'year': year, 'title': title})
        except ClientError as err:
            logger.error(
                "Couldn't delete movie %s. Here's why: %s: %s", title,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
       
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
    
    def delete_table(self):
        """
        Deletes the table.
        """
        try:
            self.table.delete()
            self.table = None
            print("Table deleted successfully!")
        except ClientError as err:
            logger.error(
                "Couldn't delete table. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise