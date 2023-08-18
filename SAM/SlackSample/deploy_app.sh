# Check if directory exists
if [ ! -d "./libs/python" ]; then
    mkdir libs/python
    pip3 install -r req.txt -t libs/python
fi
sam build
if [ -z "$1" ]
  then
    sam deploy --template-file template.yaml --capabilities CAPABILITY_NAMED_IAM --guided
    exit 1
  else
    sam deploy --template-file template.yaml --capabilities CAPABILITY_NAMED_IAM --guided --profile $1
    exit 1
fi
