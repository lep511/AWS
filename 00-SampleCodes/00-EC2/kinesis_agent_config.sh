sudo yum install –y https://s3.amazonaws.com/streaming-data-agent/aws-kinesis-agent-latest.amzn2.noarch.rpm

sudo sh -c 'cat <<EOF >  /etc/aws-kinesis/agent.json
{
  "flows": [
    {
      "filePattern": "/var/log/httpd/access_log",
      "deliveryStream": "delivery-stream"
    }
  ]
}
EOF'

sudo service aws-kinesis-agent start

# sudo service aws-kinesis-agent status

tail -f /var/log/httpd/access_log