#!/bin/bash

yum install wget unzip -y
CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -O chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip -d /usr/local

cat ~/.bash_profile  | grep 'export PATH=$PATH:/usr/local/chromedriver'

if [ $? -ne 0 ]
then
    echo 'export PATH=$PATH:/usr/local/chromedriver' >> ~/.bash_profile
    source ~/.bash_profile
fi

ln -sf /usr/local/chromedriver /usr/bin
