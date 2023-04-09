"""
## PoLicy for role:

{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["redshift:GetClusterCredentials"],
        "Resource": [
          "arn:aws:redshift:*:[AWS_Account]:dbname:[Redshift_Cluster_Identifier]/[Redshift_Cluster_Database]",
          "arn:aws:redshift:*:[AWS_Account]:dbuser:[Redshift_Cluster_Identifier]/[Redshift_Cluster_User]"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "redshift-data:*",
        "Resource": "*"
      }
    ]
}
"""

import sys
import os
import boto3
import json
import datetime

# initialize redshift-data client in boto3
redshift_client = boto3.client("redshift-data")

def call_data_api(redshift_client, redshift_database, redshift_user, redshift_cluster_id, sql_statement, with_event=True):
    # execute the input SQL statement
    api_response = redshift_client.execute_statement(Database=redshift_database, DbUser=redshift_user
                                                    ,Sql=sql_statement, ClusterIdentifier=redshift_cluster_id, WithEvent=True)

    # return the query_id
    query_id = api_response["Id"]
    return query_id

def check_data_api_status(redshift_client, query_id):
    desc = redshift_client.describe_statement(Id=query_id)
    status = desc["Status"]

    if status == "FAILED":
        raise Exception('SQL query failed:' + query_id + ": " + desc["Error"])
    return status.strip('"')

def get_api_results(redshift_client, query_id):
    response = redshift_client.get_statement_result(Id=query_id)
    return response

def lambda_handler(event, context):
    redshift_cluster_id = os.environ['redshift_cluster_id']
    redshift_database = os.environ['redshift_database']
    redshift_user = os.environ['redshift_user']

    action = event['queryStringParameters'].get('action')
    try:
        if action == "execute_report":
            country = event['queryStringParameters'].get('country_name')
            # sql report query to be submitted
            sql_statement = "select c.c_mktsegment as customer_segment,sum(o.o_totalprice) as total_order_price,extract(year from o.o_orderdate) as order_year,extract(month from o.o_orderdate) as order_month,r.r_name as region,n.n_name as country,o.o_orderpriority as order_priority from public.orders o inner join public.customer c on o.o_custkey = c.c_custkey inner join public.nation n on c.c_nationkey = n.n_nationkey inner join public.region r on n.n_regionkey = r.r_regionkey where n.n_name = '"+ country +"' group by 1,3,4,5,6,7 order by 2 desc limit 10"
            api_response = call_data_api(redshift_client, redshift_database, redshift_user, redshift_cluster_id, sql_statement)
            return_status = 200
            return_body = json.dumps(api_response)

        elif action == "check_report_status":            
            # query_id to input for action check_report_status
            query_id = event['queryStringParameters'].get('query_id')            
            # check status of a previously executed query
            api_response = check_data_api_status(redshift_client, query_id)
            return_status = 200
            return_body = json.dumps(api_response)

        elif action == "get_report_results":
            # query_id to input for action get_report_results
            query_id = event['queryStringParameters'].get('query_id')
            # get results of a previously executed query
            api_response = get_api_results(redshift_client, query_id)
            return_status = 200
            return_body = json.dumps(api_response)

            # total number of rows
            nrows=api_response["TotalNumRows"]
            # number of columns
            ncols=len(api_response["ColumnMetadata"])
            print("Number of rows: %d , columns: %d" % (nrows, ncols) )

            for record in api_response["Records"]:
                print (record)
        else:
            return_status = 500
            return_body = "Invalid Action: " + action
        return_headers = {
                        "Access-Control-Allow-Headers" : "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET"}
        return {'statusCode' : return_status,'headers':return_headers,'body' : return_body}
    except NameError as error:
        raise NameError(error)
    except Exception as exception:
        error_message = "Encountered exeption on:" + action + ":" + str(exception)
        raise Exception(error_message)