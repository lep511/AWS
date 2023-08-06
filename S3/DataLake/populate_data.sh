read -p "Landing Zone Bucket Name: " lan_zone_bucket
read -p "Raw data Bucket Name: " raw_data_bucket
read -p "Stage data Bucket Name: " stg_data_bucket
read -p "Analytics data Bucket Name: " ana_data_bucket

# Create twos 1KB files
dd if=/dev/urandom of=products_20210301.csv bs=1 count=0 seek=1K  
dd if=/dev/urandom of=file_sample.snappy.parquet bs=1 count=0 seek=1K  

# Upload file to LANDING ZONE
# format: bucket/source/region/table/year=yyyy/month=mm/day=dd/table_yyyyMMdd.csv
aws s3 cp products_20210301.csv s3://$lan_zone_bucket/socialmedia/us/tb_products/year=2019/month=05/day=16/products_20210301.csv

# Upload file to RAW DATA
# format: bucket/source/region/table/year=yyyy/month=mm/day=dd/table_yyyyMMdd.csv
aws s3 cp products_20210301.csv s3://$raw_data_bucket/socialmedia/us/tb_products/year=2019/month=05/day=16/products_20210301.csv

# Upload file to STAGE DATA
# format: bucket/source/region/bussiness_unit/table/<partitions>/table_<table_name>_yyyyMMdd.snappy.parquet
aws s3 cp file_sample.snappy.parquet s3://$stg_data_bucket/sap/br/customers/validated/dt=2021-03-01/table_customers_20210301.snappy.parquet

# Upload file to ANALYTICS DATA
# format: bucket/region/bussiness_unit/tb_<region>_<table_name>_<file_format>/<partition_0>/<partition_1>/../<partition_n>/xxxxx.compression.extension
aws s3 cp file_sample.snappy.parquet s3://$ana_data_bucket/us/sales/tb_us_customers_parquet/year=2021/month=03/day=01/part-00001-20218c886790.c000.snappy.parquet

rm products_20210301.csv
rm file_sample.snappy.parquet