from re import error
from awswrangler import dynamodb as wr
from botocore.exceptions import ClientError

def read_items(boto3_session, table_name, **kwargs):
    """
    Read items from a table.
    :param kwargs: Keyword arguments to pass to the scan method.
    :return: Items matching the search.
    """
    try:
        args = {
            "boto3_session": boto3_session, 
            "table_name" : table_name, 
            "as_dataframe" : True
        }
        response = wr.read_items(**args, **kwargs)
        return response

    except ClientError as err:
        logger.error(
            f"Couldn't read items from {self.table_name}. Here's why: {err.response['Error']['Code']} \
            {err.response['Error']['Message']}")
        raise