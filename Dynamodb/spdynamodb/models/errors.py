from botocore.exceptions import ClientError

def handle_error(error):
    if isinstance(error, str):
        print("ERROR: " + error)
    else:
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']

        print(f'[ERROR] {error_code}. {error_message}')