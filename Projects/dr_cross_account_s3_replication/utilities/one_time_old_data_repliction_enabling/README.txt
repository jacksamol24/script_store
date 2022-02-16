Description:
Once the AWS Technical Support team allows existing object replication
This script configures to replicate existing object for all the mentioned buckets in csv

It requires source and destination bucket names
and in template.json - role can be updated with the new one if different aws account is used

Steps:
1. Setup AWS environment credentials where script is going to run
1. Run Project dr_cross_account_s3_replication - main.py

2. Get the list of S3 buckets as output in the csv file name it (S3.csv)
   eg csv file:
	Bucket Name,Replica_BucketName
	model-dev,dr-model-dev
	model-prod,dr-model-prod

3. Go to directory where run.sh is present
  - Run command to make run.sh executable
	 chmod +x run.sh
  - Execute shell script
     ./run.sh
	 or
	 bash run.sh