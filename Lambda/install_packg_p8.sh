read -p "Install python 3.8? (Y/n) " installpy
read -p "Enter name layer: " namelayer
read -p "Enter package to install or [req.txt]: " packg
read -p "Enter description: " description
read -p "Enter region: " region

if [[ "$installpy" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    cwd=$(pwd)
    cd
    sudo yum update -y
    sudo amazon-linux-extras install docker -y
    sudo amazon-linux-extras install python3.8
    curl -O https://bootstrap.pypa.io/get-pip.py
    python3.8 get-pip.py --user
    cd $cwd
fi

mkdir -p python

if [[ -z "$packg" ]]; then
    python3.8 -m pip install -r req.txt -t python/
else
    python3.8 -m pip install $packg -t python/
fi

zip -r layer.zip python

if [[ -z "$description" ]]; then
    aws lambda publish-layer-version --layer-name $namelayer --zip-file fileb://layer.zip --compatible-runtimes python3.8 --region $region
else
    aws lambda publish-layer-version --layer-name $namelayer --description "$description" --zip-file fileb://layer.zip --compatible-runtimes python3.8 --region $region
fi
