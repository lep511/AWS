# Check if directory exists
if [ ! -d "./libs/python" ]; then
    mkdir libs/python
    pip3 install -r req.txt -t libs/python
fi
sam build
sam deploy --template-file template.yaml --capabilities CAPABILITY_NAMED_IAM --guided
