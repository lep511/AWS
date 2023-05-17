#!/bin/bash

read -p "Repository Name: " repository_name
aws codecommit create-repository --repository-name $repository_name
pip install --upgrade -q git-remote-codecommit

read -p "Enter your git username: " git_username
read -p "Enter your git email: " git_email
git config --global user.name $git_username
git config --global user.email $git_email

git init -b main
echo -e "\n\n.aws-sam" >> .gitignore
echo -e "samconfig.toml" >> .gitignore
git add .
git commit -m "Initial commit"

git remote add origin codecommit://$repository_name

git push -u origin main