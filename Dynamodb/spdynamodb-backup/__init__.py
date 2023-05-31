from ._queries import query_main, query_partiql_main
from ._errors import handle_error
from decimal import Decimal
from io import BytesIO
from datetime import datetime
import time
import json
import gzip
import boto3
import pandas as pd
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, TypeVar, Union, cast
from boto3.dynamodb.types import Binary
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

__version__ = "1.4.0"

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class DynamoTable:
    min_compress = 250
    
    def __init__(self, table_name=None, profile_name=None, region_name='us-east-1'):
        """
        :param table_name: A DynamoDB table.
        """
        self.table_name = table_name
        self.session = boto3.Session(profile_name=profile_name, region_name=region_name)
        self.dyn_resource = self.session.resource("dynamodb", region_name=region_name)
        self.region = region_name
        self.__keyType = {"S": "s", "N": 0, "B": b"b"}
        if not table_name:
            self.table_name = None
        elif not self.table_exists(table_name):
            print(
                "Table %s doesn't exist. To create use create_table() function.",
                table_name)
            self.table_name = None
            raise ValueError("Table doesn't exist. To create use create_table() function.")
        else:
            self.select_table(table_name)
            self.status_pitr = status_pitr
            self.delete_protection = delete_protection
            self.status_stream = status_stream
        
    def __repr__(self):
        if self.table_name != None:
            self.table.reload()
            rep = f"- Table name: {self.table_name}\
            \n- Table arn: {self.table.table_arn}\
            \n- Table creation: {self.table.creation_date_time.strftime('%Y-%m-%d %H:%M:%S')}\
            \n- {self.table.key_schema}\
            \n- {self.table.attribute_definitions}\
            \n- Point-in-time recovery status: {self.status_pitr}  |  Delete protection: {self.delete_protection}"
            if self.status_stream != "OFF":
                rep += f"\n- Stream enabled: True  |  Stream view type: {self.table.stream_specification['StreamViewType']}"
        else:
            rep = "The table has not yet been selected"
        return rep
    
    def table_exists(self, table_name):
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
                print(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        return exists
    
    def select_table(self, table_name):
        if not self.table_exists(table_name):
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
            print("Table created successfully!")

        except ClientError as err:
            print(
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
            print(
                f"Couldn't load data from {json_file} or the file does not exist.")
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
            print(
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
            print(
                "Couldn't add item to table %s. Here's why: %s: %s",
                self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def scan_att(self, att_name, query, to_pandas=False, consumed_capacity=False, pages=None):
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
            print(
                "Couldn't update movie %s in table %s. Here's why: %s: %s",
                title, self.table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Attributes']
    
    
    def query(self, pk_value, sk_value=None, index_name=None, consistent_read=False, consumed_capacity=None, to_pandas=False):
        """
        Queries an Amazon DynamoDB table and returns the matching items.
        :param pk_value: Primary key value.
        :param sk_value: Sort key value if exist. Default: None.
        :param index_name: The name of the index to query. If None, then the table itself is queried.
        :param consistent_read: If True, then a strongly consistent read is used.
        :param consumed_capacity: Return the consumed capacity. Valid values: None, "TOTAL", "INDEXES". Default: None.
        :param to_pandas: If True, returns a pandas DataFrame. Default: True.
        :return: The item/items matching the query.
        """
        response = query_main(self.table, pk_value, sk_value, index_name, consistent_read, consumed_capacity)
        
        if to_pandas:
            if not isinstance(response, list):
                return pd.DataFrame([response])
            else:
                return pd.DataFrame(response)
                
        return response
    
    
    def query_partiql(self, query, consumed_capacity=None):
        """
        Query a table using PartiQL.
        :param query: The query to execute (statement).
        :param consumed_capacity: Return the consumed capacity. Valid values: None, "TOTAL", "INDEXES". Default: None.
        :return: The query results.
        """     
        resp = query_partiql_main(query=query, consumed_capacity=consumed_capacity, dyn_table=self.table)
        return resp
                      

    def make_backup(self, backup_name=None):
        """
        Create a backup of a DynamoDB table.
        :param backup_name: The name of the backup. Default: <table_name>-<date>
        """
        if backup_name is None:
            backup_name = f"{self.table_name}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        try:
            response = self.table.meta.client.create_backup(
                TableName=self.table_name,
                BackupName=backup_name
            )
        except ClientError as err:
            print(
                f"Couldn't create a backup for {self.table_name}. Here's why: {err.response['Error']['Code']} \
                {err.response['Error']['Message']}")
            raise
        else:
            print(f"Backup {backup_name} created successfully.")
            return response

    @property
    def delete_protection(self):
        """
        Get the status of deletion protection for a DynamoDB table.
        """
        try:
            response = self.table.meta.client.describe_table(
                TableName=self.table_name
            )
        except ClientError as err:
            print(
                f"Couldn't get the status of deletion protection for {self.table_name}. Here's why: \
                {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            return response['Table']['DeletionProtectionEnabled']
    
    @delete_protection.setter
    def delete_protection(self, value):
        """
        Set deletion protection for a DynamoDB table.
        :param value: The value to set deletion protection to. Must be either True or False.
        """
        if not isinstance(value, bool):
            raise TypeError("The value must be either True or False.")
        
        if self.delete_protection == value:
            print(f"Deletion protection for {self.table_name} is already set to {value}.")
            return
        
        try:
            response = self.table.meta.client.update_table(
                TableName=self.table_name,
                DeletionProtectionEnabled = value
            )
        except ClientError as err:
            print(
                f"Couldn't set deletion protection for {self.table_name}. Here's why: \
                {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            print(f"Deletion protection for {self.table_name} set to {value}.")
    
    @property
    def status_pitr(self):
        """
        Get the status of point-in-time recovery for a DynamoDB table.
        """
        try:
            response = self.table.meta.client.describe_continuous_backups(
                TableName=self.table_name
            )
        except ClientError as err:
            print(
                f"Couldn't get the status of point-in-time recovery for {self.table_name}. Here's why: \
                {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            return response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']

    @status_pitr.setter
    def status_pitr(self, value):
        """
        Turn on point-in-time recovery for a DynamoDB table.
        :param value: The value to set point-in-time recovery to. Must be either 'ENABLED' or 'DISABLED'.
        """
        if value == "ENABLED":
            point_in_time_recovery = True
        elif value == "DISABLED":
            point_in_time_recovery = False
        else:
            raise ValueError("Value must be either 'ENABLED' or 'DISABLED'")
        
        if self.status_pitr == value:
            print(f"Point-in-time recovery is already {value}.")
            return
        try:
            response = self.table.meta.client.update_continuous_backups(
                TableName=self.table_name,
                PointInTimeRecoverySpecification={
                    'PointInTimeRecoveryEnabled': point_in_time_recovery
                }
            )
            print(f"Point-in-time recovery turned on successfully.")
            self.status_pitr = value
        except ClientError as err:
            print(
                f"Couldn't turn on point-in-time recovery for {self.table_name}. Here's why: \
                {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
    
    @property
    def status_stream(self):
        """
        Get the status of DynamoDB streams for a DynamoDB table.
        """
        try:
            response = self.table.stream_specification
        except ClientError as err:
            print(
                f"Couldn't get the status of DynamoDB streams for {self.table_name}. Here's why: \
                {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            if response:
                self.stream_arn = self.table.latest_stream_arn
                return response['StreamViewType']
            else:
                return "OFF"
        
    @status_stream.setter
    def status_stream(self, value):
        """
        Set DynamoDB streams for a DynamoDB table.
        :param value: The value to set DynamoDB streams to. Acceptable values are:
          - "ON": Turn on DynamoDB streams and set the stream view type to NEW_AND_OLD_IMAGES.
          - "KEYS_ONLY": Turn on DynamoDB streams and set the stream view type to KEYS_ONLY.
          - "NEW_IMAGE": Turn on DynamoDB streams and set the stream view type to NEW_IMAGE.
          - "OLD_IMAGE": Turn on DynamoDB streams and set the stream view type to OLD_IMAGE.
          - "NEW_AND_OLD_IMAGES": Turn on DynamoDB streams and set the stream view type to NEW_AND_OLD_IMAGES.
          - "OFF": Turn off DynamoDB streams.
        """
        value = value.upper()
        acceptable_values = ["ON", "KEYS_ONLY", "NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES", "OFF"]
               
        if value not in acceptable_values:
            print(f"Value must be one of {acceptable_values}.")
            return
        
        if value == "ON": 
            value = "NEW_AND_OLD_IMAGES"
        
        if self.status_stream == value:
            print(f"DynamoDB streams are already {value}.")
            return # No need to do anything if the value is already set to what we want.
        
        if value != "OFF" and self.status_stream == "OFF":
            try:
                response = self.table.update(
                    StreamSpecification={
                        'StreamEnabled': True,
                        'StreamViewType': value
                    }
                )
                self.stream_arn = self.table.latest_stream_arn
                print(f"DynamoDB streams turned on successfully.")
            
            except ClientError as err:
                if err.response['Error']['Code'] == 'ResourceInUseException':
                    print("A stream status change is currently in progress. Please try again later.")
                    return
                else:
                    print(
                        f"Couldn't turn on DynamoDB streams for {self.table_name}. Here's why: \
                        {err.response['Error']['Code']} {err.response['Error']['Message']}")
                raise
        elif value == "OFF":
            try:
                response = self.table.update(
                    StreamSpecification={
                        'StreamEnabled': False
                    }
                )
                self.stream_arn = None
                print(f"DynamoDB streams turned off successfully.")
            except ClientError as err:
                print(
                    f"Couldn't turn off DynamoDB streams for {self.table_name}. Here's why: \
                    {err.response['Error']['Code']} {err.response['Error']['Message']}")
                raise
        else:
            print(f"DynamoDB streams are already {self.status_stream}. You must turn them off before changing the stream view type.")
            return    
        
    
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
            print(
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