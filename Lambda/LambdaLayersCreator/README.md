## Lambda Layers Creator

### Clone the repository
git clone https://github.com/lep511/AWS.git

### Change directory
cd aws-lambda-sample/

### Write req.txt file
cat > req.txt << EOF
cryptography
aws-encryption-sdk
EOF

### Run the script
bash create_lambdafunc_p9.sh