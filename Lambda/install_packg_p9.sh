read -p "Install python 3.9? (Y/n) " installpy
read -p "Enter name layer: " namelayer
read -p "Enter package to install or [req.txt]: " packg
read -p "Enter description: " description
read -p "Enter region: [us-east-1]" region

if [[ "$installpy" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    cwd=$(pwd)
    cd
    sudo yum update -y
    sudo amazon-linux-extras install docker -y
    sudo yum -y groupinstall "Development Tools"
    sudo yum -y install openssl-devel bzip2-devel libffi-devel
    sudo yum -y install wget
    wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
    tar xvf Python-3.9.10.tgz
    cd Python-*/
    ./configure --enable-optimizations
    sudo make altinstall
    python3.9 -m pip install --upgrade pip
    cd $cwd
fi

if [[ -z "$region" ]]; then
    export region=us-east-1
fi

mkdir -p python

if [[ -z "$packg" ]]; then
    python3.9 -m pip install -r req.txt -t python/
else
    python3.9 -m pip install $packg -t python/
fi

zip -r layer.zip python

if [[ -z "$description" ]]; then
    aws lambda publish-layer-version --layer-name $namelayer --zip-file fileb://layer.zip --compatible-runtimes python3.9 --region $region
else
    aws lambda publish-layer-version --layer-name $namelayer --description "$description" --zip-file fileb://layer.zip --compatible-runtimes python3.9 --region $region
fi