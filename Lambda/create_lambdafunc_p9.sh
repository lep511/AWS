read -p "Install python 3.9? (Y/n) " installpy
read -p "Enter the lambda function name: " lambdaname
read -p "Enter package to install or [req.txt]: " packg
read -p "Enter IAM role ARN: " role
read -p "Enter handler: [lambda_function.lambda_handler] " handler


if [[ "$installpy" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    cwd=$(pwd)
    cd
    sudo yum update -y
    sudo amazon-linux-extras install docker -y
    sudo yum -y groupinstall "Development Tools"
    sudo yum -y install openssl-devel bzip2-devel libffi-devel
    sudo yum -y install wget
    wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
    tar xvf Python-3.9.10.tgz
    cd Python-*/
    ./configure --enable-optimizations
    sudo make altinstall
    python3.9 -m pip install --upgrade pip
    cd $cwd
fi


if [[ -z "$handler" ]]; then
    export handler=lambda_function.lambda_handler
fi

if [[ -z "$packg" ]]; then
    python3.9 -m pip install -r req.txt -t package/
else
    python3.9 -m pip install $packg -t package/
fi

cd package
zip -9 -r ../my-deployment-package.zip .
cd ..
zip -g my-deployment-package.zip *.py
filesize=$(wc -c my-deployment-package.zip | awk '{print $1}')

if [ "$filesize" -gt 50000000 ]; then
    BUCKET_ID=$(dd if=/dev/random bs=8 count=1 2>/dev/null | od -An -tx1 | tr -d ' \t\n')
    BUCKET_NAME=temp-lambda-function-$BUCKET_ID
    aws s3 mb s3://$BUCKET_NAME
    aws s3 cp my-deployment-package.zip s3://$BUCKET_NAME
    size=$(expr $filesize / 256000)
    aws lambda create-function --function-name $lambdaname\
    --runtime python3.9\
    --role $role\
    --handler $handler\
    --memory-size $size\
    --publish --code S3Bucket=$BUCKET_NAME,S3Key=my-deployment-package.zip
    
    aws s3 rm s3://$BUCKET_NAME --recursive
    aws s3api delete-bucket --bucket $BUCKET_NAME
else
    aws lambda create-function --function-name $lambdaname\
        --runtime python3.9\
        --role $role\
        --handler $handler\
        --publish --zip-file fileb://my-deployment-package.zip
fi
