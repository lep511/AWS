import boto3

source_bucket = "sfw-module-distributed-m-distributedmapworkshopda-1696l493e9ncj"
source_prefix = "1929/"
destination_bucket = "sfw-module-distributed-m-distributedmapworkshopda-1696l493e9ncj"
destination_prefix = "1929/"
sse_kms_key_id = "arn:aws:kms:us-east-1:435924829664:key/ae9001c0-f93e-4f89-97e5-14ff60eb2329"

# Crear una instancia del cliente de S3
s3_client = boto3.client("s3")

# Copiar objetos de origen a destino recursivamente
response = s3_client.copy_object(
    CopySource={"Bucket": source_bucket, "Key": source_prefix},
    Bucket=destination_bucket,
    Key=destination_prefix,
    MetadataDirective="COPY",
    ServerSideEncryption="aws:kms",
    SSEKMSKeyId=sse_kms_key_id,
    CopySourceSSECustomerKey="aws:kms"
)

print("Objetos copiados exitosamente:", response)
