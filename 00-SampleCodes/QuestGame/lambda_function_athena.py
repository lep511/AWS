import boto3
import json

def lambda_handler(event, context):
    # Create an Athena client using boto3
    athena = boto3.client('athena')
    
    # SQL query to execute
    sql = 'SELECT * FROM table_name'
    
    # Execute the query
    response = athena.start_query_execution(
        QueryString=sql,
        ResultConfiguration={'OutputLocation': 's3://bucket_name/path/'}
    )
    
    # Get the query execution ID
    query_execution_id = response['QueryExecutionId']
    
    # Get query results
    query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
    query_exec_status = query_status['QueryExecution']['Status']['State']
    if query_exec_status == 'SUCCEEDED':
        query_results = athena.get_query_results(QueryExecutionId=query_execution_id)
        print(query_results)
    else:
        print('Query failed to execute')
        return {"statusCode": 400, "body": json.dumps('Query failed to execute')}
    
    return {"statusCode": 200, "body": json.dumps('Query executed successfully')}

    
        