# syntax=docker/dockerfile:1
FROM amazonlinux:latest
RUN yum -y install which unzip python3 python3-pip aws-cli
FROM python:3.8-slim-buster
RUN python3 -m pip install boto3 flask
RUN python3 -m pip install amazon-dax-client
WORKDIR /python-docker
COPY . .
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]