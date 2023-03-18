sudo amazon-linux-extras install epel -y
sudo yum install stress -y
sudo stress-ng --cpu 4 -v - timeout 60s