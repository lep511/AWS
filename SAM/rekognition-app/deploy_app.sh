#pip3 install -r requirements.txt -t libs/python
sam build
sam deploy --template-file template.yaml --capabilities CAPABILITY_NAMED_IAM --guided
