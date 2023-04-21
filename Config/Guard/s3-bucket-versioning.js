rule check_bucketversioning {
     supplementaryConfiguration.BucketVersioningConfiguration.status == "Enabled" <<
     result: NON_COMPLIANT
     message: S3 Bucket Versioning is NOT enabled.
     >>
}
