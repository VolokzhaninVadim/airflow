# Docker (Ubuntu)
```
# Install packages for work with net
sudo apt install net-tools
sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common
# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=arm64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
apt-cache policy docker-ce
sudo apt-get -y install docker-ce
# Add user in docker group, that do not launch docker with sudo
sudo usermod -aG docker ${USER}
# Install docker-compose
sudo apt install python3-pip
sudo pip3 install docker-compose
```

# Airflow
![airflow_64x64_emoji_transparent.png](https://cwiki.apache.org/confluence/download/attachments/145723561/airflow_64x64_emoji_transparent.png)
