# This is importing all the required libraries and modules.
import boto3
import json
import os
import urllib.errorimport urllib.request

from flask import Flask, redirect, url_for, request, flash, send_file, abort
from flask import render_template
from werkzeug.utils import secure_filename

from s3 import s3_upload_files, list_s3_objects, delete_objects, download_objects
from util import dynamodb_client, dynamodb_resource, create_table, list_dynamodb_tables, \
    query_document, list_table_items , add_items_in_table
from flask_caching import Cache
from rds import add_data

# This is a configuration for the Flask application.
config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 120
}
application = Flask(__name__)

# This is to get the region and instance name of the EC2 instance.
try:
    doc = urllib.request.urlopen("http://169.254.169.254/latest/dynamic/instance-identity/document", timeout=1).read()
except urllib.error.URLError:
    doc = None

# This is to get the region and instance name of the EC2 instance.
if doc:
    application.config['REGION'] = json.loads(doc)['availabilityZone']
    region = json.loads(doc)["region"]
    instance_id = json.loads(doc)["instanceId"]
    ec2 = boto3.resource('ec2', region)
    ec2instance = ec2.Instance(instance_id)
    instance_name = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instance_name = tags["Value"]
    application.config['INSTANCE_NAME'] = instance_name
else:
    region = 'us-east-1'
    application.config['REGION'] = "unknown region"
    application.config['INSTANCE_NAME'] = "unknown name"

# This is a configuration for the Flask application.
query_count = 0
application.secret_key = os.urandom(24)
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'png'}
# dynamodb_client = boto3.client('dynamodb')
bucket_name = os.environ.get('BUCKET_NAME')
dynamodb_table_name = 'customer_table'


def allowed_file(filename):
    """
    If the file extension is in the list of allowed extensions, return True

    :param filename: The name of the file that was uploaded
    :return: a boolean value.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def query_increment():
    """
    It increments the global variable `query_count` by 1
    """
    global query_count
    query_count = query_count + 1


@application.route('/', methods=['GET', 'POST'])
def index():
    """
    If the bucket is empty, render the main.html template. If the bucket is not empty, redirect to the files.html template.
    :return: the rendered template 'main.html'
    """
    if request.method in 'POST':
        print(f"*** Inside the template")
    try:
        if list_s3_objects(bucket_name):
            return redirect(url_for('files'))
        else:
            return render_template('main.html')
    except Exception as e:
        flash(f' *** Error: {e}', 'danger')
        return render_template('main.html')


@application.route('/files')
def files():
    """
    It queries the DynamoDB table for all entries, then renders the files.html template with the results of the S3 query and
    the DynamoDB query
    :return: The files.html template is being returned.
    """
    client = dynamodb_client()
    results = list_s3_objects(bucket_name)
    if results:
        query_increment()
        try:
            forms = client.execute_statement(Statement="SELECT * from customer_table;")
            entries = forms['Items']
            print(entries)

            return render_template('files.html', files=results, entries=entries)
        except Exception as e:
            print(f"error:{e}")
            flash(f' *** No DynamoDB table Found', 'danger')
            return render_template('files.html', files=results)
    else:
        return render_template('main.html')


@application.route('/upload_files_to_s3', methods=['GET', 'POST'])
def upload_files_to_s3():
    """
        The function uploads the file to S3 bucket and then queries the document using Textract.

        The results are then stored in a table in the database.

        The function then redirects to the files page.
        :return: the file_to_upload, bucket_name, file_name, and content_type.
    """
    if request.method == 'POST':

        # No file selected
        if 'file' not in request.files:
            flash(f' *** No files Selected', 'danger')

        file_to_upload = request.files['file']
        content_type = request.mimetype

        # if empty files
        if file_to_upload.filename == '':
            flash(f' *** No files Selected', 'danger')

        # file uploaded and check
        if file_to_upload and allowed_file(file_to_upload.filename):

            file_name = secure_filename(file_to_upload.filename)

            print(f" *** The file name to upload is {file_name}")
            print(f" *** The file full path  is {file_to_upload}")

            s3_upload_files(file_to_upload, bucket_name, file_name, content_type)
            flash(f'Success - {file_to_upload} Is uploaded to {bucket_name} bucket', 'success')

            try:
                items = query_document(bucket_name,file_name,region)
                items = json.loads(items)
                # print(items)
                if items:
                    try:
                        create_table("customer_table")
                    except Exception as e:
                        print(f" *** Error: {e}")
                        add_items_in_table("customer_table",items)
                    return redirect(url_for('files'))
                else:
                    print("nothing to do!")
            except Exception as e:
                print(f"error:{e}")
                flash(f"Failed to analyze document. Reason: {e}")

        else:
            flash(f'Allowed file type are - jpg and png.Please upload proper formats...', 'danger')
            return redirect(url_for('files'))
    return redirect(url_for('files'))


@application.route('/delete_objects', methods=['POST'])
def delete():
    """
    This function takes the key of the file to be deleted from the form, and then calls the delete_objects function from the
    s3_functions.py file.

    If the response is successful, it flashes a success message and redirects to the files page.

    If the response is unsuccessful, it flashes a danger message and redirects to the main page.

    If the bucket is empty, it redirects to the main page.
    :return: the response from the delete_objects function.
    """
    key = request.form['key']
    response = delete_objects(bucket_name, key)
    if response['ResponseMetadata']['HTTPStatusCode'] == 204:
        flash(f'Success - File Is Deleted from {bucket_name} bucket', 'success')
    else:
        flash(f'Could not delete the file...', 'danger')
        return render_template('main.html')

    if list_s3_objects(bucket_name):
        return redirect(url_for('files'))
    else:
        return render_template('main.html')


@application.route('/download_objects', methods=['POST'])
def download():
    """
    It downloads the file from the S3 bucket and sends it to the user
    :return: The file is being returned as a response.
    """
    key = request.form['key']
    response = download_objects(bucket_name, key)
    if response:
        flash(f'Success - File {key} Downloaded', 'success')
    else:
        flash(f'Could not download the file...', 'danger')
    return send_file(response, as_attachment=True)


@application.route("/<full_name>")
def items(full_name):
    """
    This function takes in a full name as a parameter and returns a list of all the forms that the customer has filled out

    :param full_name: The name of the customer you want to query
    :return: The items_data is being returned.
        """
    print(full_name)
    query_increment()
    form_list = []
    client = dynamodb_client()
    item_query = client.execute_statement(Statement="SELECT * from customer_table;")
    print(item_query)
    print(type(item_query))
    for c in item_query['Items']:
        borrower_name = c["Borrower Name"]['S']
        print(borrower_name)
        if borrower_name == full_name:
            form_list.append(borrower_name)
            print(f"formlist: {form_list}")


    if len(form_list) < 1:
        abort(404)

    query_increment()
    form_data = client.execute_statement(Statement="SELECT * from customer_table;")
    items_data = form_data['Items']

    for item in items_data:
        borrowerName = item["Borrower Name"]['S']
        loanRequested = item["Loan Requested"]['S']
        propertyValue = item["Property Value"]['S']
        propertyAddress = item["Property Address"]['S']
        loanOfficer = item["Loan Officer"]['S']
        add_data(borrowerName, loanRequested, propertyValue, propertyAddress, loanOfficer)

    return render_template('query.html', items=items_data)


# This is the main function that is being called when the application is being run.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.config.from_mapping(config)
    application.run(host='0.0.0.0', port=80)