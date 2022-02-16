#!/bin/bash
# Install Spark on CentOS 7/8
set -e
cd /root

yum install java -y
java -version

spark_version="2.4.2"

yum install wget -y
wget https://downloads.lightbend.com/scala/2.13.2/scala-2.13.2.tgz
tar xvf scala-2.13.2.tgz
mv scala-2.13.2 /usr/lib
ln -s /usr/lib/scala-2.13.2 /usr/lib/scala
export PATH=$PATH:/usr/lib/scala/bin
scala -version

wget "https://github.com/ojdkbuild/contrib_jdk8u-ci/releases/download/jdk8u262-b10/jdk-8u262-ojdkbuild-linux-x64.zip"
unzip "jdk-8u262-ojdkbuild-linux-x64.zip"

wget "https://archive.apache.org/dist/spark/spark-$spark_version/spark-$spark_version-bin-hadoop2.7.tgz"
tar xvfz "spark-$spark_version-bin-hadoop2.7.tgz"

wget "https://archive.apache.org/dist/hadoop/core/hadoop-2.7.3/hadoop-2.7.3-src.tar.gz"
tar xvfz "hadoop-2.7.3-src.tar.gz"

echo 'export PATH=$PATH:/usr/lib/scala/bin' >> .bash_profile

spark_home_export="export SPARK_HOME=$HOME/spark-$spark_version-bin-hadoop2.7"
echo $spark_home_export >> .bash_profile
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> .bash_profile

hadoop_home_export="export HADOOP_HOME=$HOME/hadoop-2.7.3-src"
echo $hadoop_home_export >> .bash_profile
echo 'export PATH=$PATH:$HADOOP_HOME/bin' >> .bash_profile

java_home_export="export JAVA_HOME=$HOME/jdk-8u262-ojdkbuild-linux-x64"
echo $java_home_export >> .bash_profile
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> .bash_profile
