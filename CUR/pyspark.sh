sudo apt-get update -y
sudo apt install default-jdk -y
sudo apt install default-jre -y

pip install --upgrade pip -q

pip install --upgrade boto3
pip install --upgrade pyspark
pip install --upgrade pandas
pip install --upgrade PyArrow 

export JAVA_HOME="/usr"
export PYARROW_IGNORE_TIMEZONE=1
