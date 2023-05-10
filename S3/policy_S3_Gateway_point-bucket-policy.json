{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": [
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::BUCKET/*",
            "Condition": {
                "StringNotEquals": {
                    "aws:sourceVpce": "VPCE_ID"
                }
            }
        }
    ]
}
