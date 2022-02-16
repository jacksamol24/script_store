#!/bin/bash
count=`cat S3.csv | wc -l`

for (( c=2; c<=$count+1; c++ ))
do  
   bucketname=`cat S3.csv | head -$c | tail -1 | awk -F"," {'print $1'}`
   drbucketname=`cat S3.csv | head -$c | tail -1 | awk -F"," {'print $2'}`
   
   #bucketname=`cat S3.csv | head -2 | tail -1 | awk -F"," {'print $1'}`
   #drbucketname=`cat S3.csv | head -2 | tail -1 | awk -F"," {'print $2'}`
   
   echo "$bucketname"
   echo "$drbucketname"
   cp template.json output.json
   sed "s/bucketname/$drbucketname/g" template.json > output.json
   aws s3api put-bucket-replication --bucket $bucketname --replication-configuration file://output.json
done