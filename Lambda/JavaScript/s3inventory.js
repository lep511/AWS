const aws = require('aws-sdk');
var srcBucket = null;
var dstBucket = null;
// read S3 bucket and generate s3 batch job manifest listing files that have not been encrypted
exports.handler = async (event) => {
    srcBucket = (await getSSMParameter('/SecurityWorkshop/DemoCloudTrailS3Bucket'))['Parameter']['Value'];
    dstBucket = (await getSSMParameter('/SecurityWorkshop/UtilityS3Bucket'))['Parameter']['Value'];
    var manifestData = [];
    const s3SourceBucketOptions = {
        Bucket: srcBucket,
        // ContinuationToken: 'STRING_VALUE',
        // Delimiter: 'STRING_VALUE',
        // EncodingType: url,
        FetchOwner: false,
        //MaxKeys: 500,
        // Prefix: 'STRING_VALUE',
        // RequestPayer: requester,
        // StartAfter: 'STRING_VALUE'
    };
    let s3client = new aws.S3();
    let asyncJobs = [];
    let keyList = [];

    for await (const data of listAllKeys(s3SourceBucketOptions)) {
        for (let s3Object of data.Contents) {
            keyList.push(s3Object['Key']);
            asyncJobs.push(
                s3client.headObject({
                    Key: s3Object['Key'],
                    Bucket: srcBucket
                }).promise());
        }
    }

    let asyncResults = await Promise.allSettled(asyncJobs);

    try {

        for (let index = 0; index < asyncResults.length; index++) {
            if (asyncResults[index]['status'] == 'fulfilled') {
                if (!(asyncResults[index]['value']['ServerSideEncryption'])) {
                    // the object is not encrypted
                    manifestData.push(srcBucket + ',' + keyList[index]);
                }
                else if (asyncResults[index]['value']['ServerSideEncryption'] == 'AES256') {
                    // the object is encrypted with SSE-S3
                    manifestData.push(srcBucket + ',' + keyList[index]);
                }
                else {
                    // the object is already encrypted with kms, ignore it
                    manifestData.push(srcBucket + ',' + keyList[index]);
                }

            }
        }
    }
    catch (e) {
        console.log('S3 batch manifest generation exception' + JSON.stringify(e));
    }
    finally {
        // attempt to close the file

    }

    let responseValue = manifestData.join('\n');
    // copy the object to s3 bucket
    await copyObjectToS3(dstBucket, 'manifestdata.txt', responseValue);
    return responseValue;
};


async function* listAllKeys(opts) {
    const s3 = new aws.S3();
    opts = { ...opts };
    do {
        const data = await s3.listObjectsV2(opts).promise();
        opts.ContinuationToken = data.NextContinuationToken;
        yield data;
    } while (opts.ContinuationToken);
}


function getS3HeadObject(bucket, key) {
    var params =
    {
        Key: key,
        Bucket: bucket
    };
    let s3client = new aws.S3({ apiVersion: '2006-03-01' });
    return s3client.headObject(params).promise();
}

// utility function to retreive an S3 object
function copyObjectToS3(bucketName, objectKey, content) {
    var params = {
        Key: objectKey,
        Bucket: bucketName,
        Body: Buffer.from(content, "utf8")
    };
    let s3client = new aws.S3({ apiVersion: '2006-03-01' });
    return s3client.upload(params).promise();
}


function getSSMParameter(path) {
    let ssmclient = new aws.SSM();
    var params = {
        Name: path
    };
    return ssmclient.getParameter(params).promise();

}
