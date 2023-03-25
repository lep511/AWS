<<<<<<< HEAD
# Check if a directory exists
if [ ! -d "libs/python" ]; then
=======
# Check if directory exists
if [ ! -d "./libs/python" ]; then
    mkdir libs/python
>>>>>>> cd34ccebdf7723b193f1e4c37882cd540e3078c8
    pip3 install -r requirements.txt -t libs/python
fi
sam build
sam deploy --template-file template.yaml --capabilities CAPABILITY_NAMED_IAM --guided
