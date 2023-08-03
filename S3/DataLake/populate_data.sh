read -p "Landing Zone Bucket Name: " landing_zone_bucket
read -p "Raw data Bucket Name: " raw_data_bucket
read -p "Stage data Bucket Name: " stage_data_bucket
read -p "Analytics data Bucket Name: " analytics_data_bucket

# Create 1KB file
dd if=/dev/urandom of=fake_data.file bs=1 count=0 seek=1K  

# Upload file to landing zone
aws s3 cp fake_data.file s3://$landing_zone_bucket/source/us/tb_costumer/year=2019/month=05/day=16/fake_data.file

# Upload file to raw data
aws s3 cp fake_data.file s3://$raw_data_bucket/source/us/tb_transactions/year=2020/month=01/day=12/fake_data.file

# Upload file to stage data
aws s3 cp fake_data.file s3://$stage_data_bucket/source/us/tb_products/year=2021/month=12/day=15/fake_data.file

# Upload file to analytics data
aws s3 cp fake_data.file s3://$analytics_data_bucket/source/us/tb_costumer/year=2019/month=05/day=16/fake_data.file

rm fake_data.file