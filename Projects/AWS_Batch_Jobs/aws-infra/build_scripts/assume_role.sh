#!/bin/bash
#on-commit_test
account_id=<aws-account-id>
role="<role_name>"
tmp_credential_file=./tmp_credential_file
role_arn="arn:aws:iam::${account_id}:role/${role}"
echo ${role_arn}

resp=$(aws sts assume-role  --role-arn "${role_arn}" --duration-seconds 3600 \
--role-session-name "credential_session") || { echo "cant assume role"; exit 33; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
cat <<EOF > ${tmp_credential_file}
export AWS_ACCESS_KEY_ID=$(echo $resp | jq -r .Credentials.AccessKeyId )
export AWS_SECRET_ACCESS_KEY=$(echo $resp | jq -r .Credentials.SecretAccessKey )
export AWS_SESSION_TOKEN=$(echo $resp | jq -r .Credentials.SessionToken )
EOF
cat $tmp_credential_file