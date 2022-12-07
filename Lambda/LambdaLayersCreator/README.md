## Lambda Layers Creator

### Clone the repository
git clone https://github.com/lep511/AWS.git

### Change directory
cd AWS/Lambda/LambdaLayersCreator/

### Write req.txt file
cat > req.txt << EOF
cryptography
aws-encryption-sdk
EOF

### Run the script
bash p9_create_lambda_layer.sh