from boto3.session import Session
import json
import boto3
import zipfile
import tempfile
import botocore
import traceback

code_pipeline = boto3.client("codepipeline")
sagemaker = boto3.client("sagemaker")


def find_artifact(job_data):
    """Finds the input artifact
    Args:
        job_data: The dictionary of job data
    Returns:
        The artifact dictionary found
    """
    try:
        artifact = job_data["inputArtifacts"][0]
        return artifact
    except:
        raise Exception("Input artifact not found")


def get_model_name(s3, artifact):
    """Gets the model name from the JSON output artifact of the training state machine
    Args:
        artifact: The artifact to download
    Returns:
        The model name as string
    """
    tmp_file = tempfile.NamedTemporaryFile()
    bucket = artifact["location"]["s3Location"]["bucketName"]
    key = artifact["location"]["s3Location"]["objectKey"]

    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, "r") as zip:
            output = json.loads(zip.read("output.json"))
            model_name = output["Model"]["Output"]["ModelArn"].split("/")[-1]
            return model_name


def create_endpoint_configuration(endpoint_config_name, model_name):
    """Create SageMaker Endpoint Configuration
    Args:
        endpoint_config_name: Name of the endpoint configuration to create
        model_name: Name of the SageMaker credit card default model
    """
    print("Creating endpoint configuration...")
    variant_name = "default"
    instance_count = 1
    instance_type = "ml.t2.medium"
    ###########################################################################
    # TODO1: Write code to create an endpoint configuration with the model name,
    # endpoint configuration name, variant name, and instance type
    ###########################################################################
    response = sagemaker.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                "VariantName": variant_name,
                "ModelName": model_name,
                "InstanceType": instance_type,
                "InitialInstanceCount": instance_count,
            }
        ],
    )
    


def create_endpoint(endpoint_name, endpoint_config_name):
    """Creates a new SageMaker Endpoint
    Args:
        endpoint_name: The endpoint name
        endpoint_config_name: The name of the endpoint configuration
    """
    if endpoint_exists(endpoint_name):
        print("Update endpoint")
        ###########################################################################
        # TODO2: Write code to update a SageMaker endpoint if it already exists
        ###########################################################################
        response = sagemaker.update_endpoint(
            EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("Endpoint updated")
        else:
            print("Endpoint update failed")

    else:
        print("Create endpoint")
        ###########################################################################
        # TODO3: Write code to create a SageMaker endpoint if does not exist
        ###########################################################################
        response = sagemaker.create_endpoint(
            EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("Endpoint created")
        else:
            print("Endpoint creation failed")
            

def endpoint_exists(endpoint_name):
    """Check if an endpoint exists or not
    Args:
        endpoint_name: The endpoint to check
    Returns:
        True or False depending on whether the endpoint exists
    """
    try:
        sagemaker.describe_endpoint(EndpointName=endpoint_name)
        return True
    except botocore.exceptions.ClientError as e:
        if "not find" in e.response["Error"]["Message"]:
            return False
        else:
            raise e


def endpoint_config_exists(endpoint_config_name):
    """Check if an endpoint configuration exists or not
    Args:
        endpoint_config_name: The endpoint configuration to check
    Returns:
        True or False depending on whether the endpoint configuration exists
    """
    try:
        sagemaker.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
        return True
    except botocore.exceptions.ClientError as e:
        if "not find" in e.response["Error"]["Message"]:
            return False
        else:
            raise e


def get_endpoint_status(endpoint_name):
    """Get the status of an existing SageMaker endpoint
    Args:
        endpoint_name: The name of the endpoint to check
    Returns:
        The endpoint status
    """
    endpoint_description = sagemaker.describe_endpoint(EndpointName=endpoint_name)
    return endpoint_description["EndpointStatus"]


def put_job_success(job, message):
    """Notify CodePipeline of a successful job
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
    """
    print("Putting job success")
    print(message)
    code_pipeline.put_job_success_result(jobId=job)


def put_job_failure(job, message):
    """Notify CodePipeline of a failed job
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    """
    print("Putting job failure")
    print(message)
    code_pipeline.put_job_failure_result(
        jobId=job, failureDetails={"message": message, "type": "JobFailed"}
    )


def continue_job_later(job, message):
    """Notify CodePipeline of a continuing job
    Args:
        job: The JobID
        message: A message to be logged relating to the job status
    """
    # Use the continuation token to keep track of any job execution state
    # This data will be available when a new job is scheduled to continue the current execution
    continuation_token = json.dumps({"previous_job_id": job})
    print("Putting job continuation")
    print(message)
    code_pipeline.put_job_success_result(
        jobId=job, continuationToken=continuation_token
    )


def check_endpoint_status(job_id, endpoint_name):
    """Monitor an already-running SageMaker endpoint creation
    Succeeds, fails or continues the job depending on the endpoint status.
    Args:
        job_id: The CodePipeline job ID
        endpoint_name: The endpoint to monitor
    """
    try:
        status = get_endpoint_status(endpoint_name)
        if status == "InService":
            # If the creation finished successfully then succeed the job and don't continue.
            put_job_success(job_id, "SageMaker endpoint creation complete")

        elif status in ["Creating", "Updating", "SystemUpdating"]:
            # If the job isn't finished yet then continue it
            continue_job_later(job_id, "SageMaker endpoint creation still in progress")

        else:
            # If the endpoint has failed, end the job with a failed result.
            put_job_failure(job_id, "Update failed: " + status)
    except:
        raise Exception(f"Unable to retrieve endpoint {endpoint_name}")


def get_user_params(job_data):
    """Decodes the JSON user parameters and validates the required properties.
    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure
    Returns:
        The JSON parameters decoded as a dictionary.
    """
    try:
        # Get the user parameters which contain the endpoint name and endpoint configuration name
        user_parameters = job_data["actionConfiguration"]["configuration"][
            "UserParameters"
        ]
        decoded_parameters = json.loads(user_parameters)
    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception("UserParameters could not be decoded as JSON")

    if "endpoint_name" not in decoded_parameters:
        # Validate that the endpoint name is provided, otherwise fail the job
        raise Exception("Your UserParameters JSON must include the endpoint name")
    if "endpoint_config_name" not in decoded_parameters:
        # Validate that the endpoint configuration name is provided, otherwise fail the job
        raise Exception(
            "Your UserParameters JSON must include the endpoint configuration name"
        )
    return decoded_parameters


def setup_s3_client(job_data):
    """Creates an S3 client
    Uses the credentials passed in the event by CodePipeline.
    Args:
        job_data: The job data structure
    Returns:
        An S3 client with the appropriate credentials
    """
    key_id = job_data["artifactCredentials"]["accessKeyId"]
    key_secret = job_data["artifactCredentials"]["secretAccessKey"]
    session_token = job_data["artifactCredentials"]["sessionToken"]
    session = Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token,
    )
    return session.client("s3", config=botocore.client.Config(signature_version="s3v4"))


def lambda_handler(event, context):
    """The Lambda function handler
    If a continuing job then checks the SageMaker endpoint status and updates the job accordingly.
    If a new job, then create the SageMaker endpoint
    Args:
        event: The event passed by Lambda
        context: The context passed by Lambda
    """
    # endpoint_config_name
    # endpoint_name
    
    # Extract the Job ID
    print("Received event: " + json.dumps(event, indent=2))
    job_id = event["CodePipeline.job"]["id"]
    # Extract the Job Data
    job_data = event["CodePipeline.job"]["data"]
    try:
        # Extract the params
        params = get_user_params(job_data)
        endpoint_config_name = params["endpoint_config_name"]
        endpoint_name = params["endpoint_name"]

        if "continuationToken" in job_data:
            # If we're continuing then the create/update has already been triggered
            # we just need to check if it has finished.
            check_endpoint_status(job_id, endpoint_name)
        else:
            # Get the artifact details
            artifact = find_artifact(job_data)
            # Get S3 client to access artifact with
            s3 = setup_s3_client(job_data)
            # Get the JSON template file out of the artifact
            model_name = get_model_name(s3, artifact)
            # Kick off a endpoint configuration and endpoint creation
            if endpoint_config_exists(endpoint_config_name):
                sagemaker.delete_endpoint_config(
                    EndpointConfigName=endpoint_config_name
                )
            create_endpoint_configuration(endpoint_config_name, model_name)
            create_endpoint(endpoint_name, endpoint_config_name)
            check_endpoint_status(job_id, endpoint_name)

    except Exception as e:
        print("Function failed due to exception.")
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))
    return "Complete"
