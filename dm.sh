read -p "Install python 3.9? (Y/n) " installpy
if [[ "$installpy" =~ ^([yY][eE][sS]|[yY][])$ ]]
then
    cd AWS
fi
