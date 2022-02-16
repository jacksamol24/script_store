FROM centos:centos8

RUN yum update -y && yum install sudo wget postgresql-devel gcc gcc-c++ dos2unix unzip atlas-devel java-1.8.0-openjdk cifs-utils git -y && yum clean all
ADD Df-install-scripts Df-install-scripts
RUN cd Df-install-scripts && dos2unix *.sh && chmod +x *.sh && ./python3_7.sh && ./python3_6.sh && pip3.7 install boto3 && ./install_chromedriver.sh && ./install_chrome.sh && ./install_aws_cli.sh && ./install_p7zip.sh && ./bcp_linux_tools.sh && ./install_spark.sh && ./install_jars.sh

ADD entry_point_scripts/* /
RUN dos2unix *.sh && chmod +x *.sh