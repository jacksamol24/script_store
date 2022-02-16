#!/bin/bash

yum install gcc openssl-devel bzip2-devel libffi-devel wget make -y
cd /usr/src
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
tar xzf Python-3.6.4.tgz
cd Python-3.6.4
./configure --enable-optimizations
make altinstall
rm -f /usr/src/Python-3.6.7.tgz
