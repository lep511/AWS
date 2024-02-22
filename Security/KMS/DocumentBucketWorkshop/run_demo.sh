# read command will prompt you to enter the name of bucket name you wish to create 
 
if [ -z "$1" ]; then
    read -r -p  "Enter the name of the bucket:" bucketname
    echo "Creating the AWS S3 bucket... "
    echo ""
    createbucket    # Calling the createbucket function  
    echo "AWS S3 bucket $bucketname created successfully"
else
    bucketname=$1
fi
 
# Creating first function to create a bucket 
 
function createbucket()

   {
    aws s3api  create-bucket --bucket $bucketname --region us-east-1
   }

python encrypt-files.py --type encrypt --directory logs
bash upload_data.sh $bucketname