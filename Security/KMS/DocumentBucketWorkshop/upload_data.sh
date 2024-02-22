if [ $# -eq 0 ]
  then
    echo "No bucket name supplied"
    exit 1
fi

python encrypt-files.py --type encrypt --directory logs
aws s3 cp logs/encrypted s3://$1/logs --recursive
aws s3 cp metadata s3://$1/logs/metadata --recursive
rm -rf logs/encrypted
rm -rf metadata
