#!/bin/bash
set -e

source ~/.bash_profile
s3_bucket_name="$2"

echo "Cloning Git repo from S3 bucket"
mkdir code_dir
/usr/local/bin/aws s3 cp s3://$s3_bucket_name code_dir/ --recursive
echo "Clone Completed"

echo "Starting $1 project job execution"

cd "code_dir/$1"
pip3.6 install --upgrade pip
pip3.6 install -r requirements.txt
python3.6 main.py "${@:3}"

echo "Project $1 job execution ended"