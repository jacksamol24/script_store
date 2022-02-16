#!/bin/bash
wget https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/p/p7zip-16.02-20.el7.x86_64.rpm
wget https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/p/p7zip-plugins-16.02-20.el7.x86_64.rpm
rpm -Uvh p7zip-16.02-20.el7.x86_64.rpm
rpm -Uvh p7zip-plugins-16.02-20.el7.x86_64.rpm