CREATE EXTERNAL TABLE my_ingested_data150 (
EVENT_TIME DATE,
TICKER_SYMBOL STRING,
CHANGE DOUBLE,
SECTOR STRING,
PRICE DOUBLE
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
with serdeproperties ( 'paths'='TICKER_SYMBOL, SECTOR, PRICE, CHANGE, EVENT_TIME' )
LOCATION "s3://my-data-stack-datas3bucket-anecwsbairom/"