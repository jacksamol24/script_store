import json
import os
import logging,sys
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from victorops_decorator import decorators

suppress_alerts = 'ROUTING_KEY' not in os.environ
routing_key = os.environ['ROUTING_KEY'] if 'ROUTING_KEY' in os.environ else None

def check_if_bucket_exist(bucket_name, list_of_current_buckets):
    '''
    Function Description:
        Function to check if bucket already exist in present bucket list
    Parameters:
        [string] bucket_name: name of the bucket to check existence
        [string] list_of_current_buckets: List of current s3 buckets available before calling this function to search from
    '''
    if bucket_name in list_of_current_buckets:
        logging.info(f"Bucket {bucket_name} already exists")
        return True
    else:
        logging.info(f"Bucket {bucket_name} does not exists")
        return False


def create_dr_bucket(s3_client, bucket_name, replica_bucket_name, region, role_name, list_of_current_buckets):
    '''
    Function Description:
        Create bucket and block public access of the bucket
    Parameters:
        [string] s3_client: AWS s3 connection session object opened before calling this function
        [string] bucket_name: Name of the bucket to create
        [string] region: aws region in which bucket needs to be created
        [string] role_name: if replication configuration needs to be updated pass rolename to that function
        [string] replica_bucket_name: name of replica bucket
        [string] list_of_current_buckets: List of current s3 buckets available before calling this function
    '''

    if not ((check_if_bucket_exist(replica_bucket_name, list_of_current_buckets))):
        try:
            if region is None:
                raise Exception("Error: region not specified to create S3 bucket")
            else:
                s3_client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=replica_bucket_name,
                                        CreateBucketConfiguration=location)
                logging.info(f"Created Bucket: {replica_bucket_name}")
        except ClientError as e:
            logging.error(e)
            return False

    s3_client.put_public_access_block(
        Bucket=replica_bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
    )

    logging.debug(f"Public access blocked - Bucket: {replica_bucket_name}")

    logging.info(f"Putting replication configuration as {replica_bucket_name} to {bucket_name}")
    put_replication_configuration(s3_client, replica_bucket_name, bucket_name, role_name)


def add_bucket_policy(s3_client, bucket_name, source_acc_role_name):
    bucket_policy = {
        "Version": "2012-10-17",
        "Id": "PolicyForDestinationBucket",
        "Statement": [
            {
                "Sid": "Permissions on objects",
                "Effect": "Allow",
                "Principal": {
                    "AWS": {source_acc_role_name}
                },
                "Action": [
                    "s3:ReplicateDelete",
                    "s3:ReplicateObject"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            },
            {
                "Sid": "Permissions on bucket",
                "Effect": "Allow",
                "Principal": {
                    "AWS": {source_acc_role_name}
                },
                "Action": [
                    "s3:List*",
                    "s3:GetBucketVersioning",
                    "s3:PutBucketVersioning"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}"
            }
        ]
    }

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    bucket_policy = json.dumps(bucket_policy, default=set_default)

    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)


def put_replication_configuration(s3_client, bucket_name, replica_bucket_name, dest_acc_role_name):
    '''
    Function Description:
        Create replication configuration for given bucket
    Parameters:
        s3_client: boto3 client created for connecting to aws account
        bucketname: Name of the bucket which needs replication with another replica bucket
        replica_bucket_name: Name of the bucket which will be added as replica bucket
        dest_acc_role_name: destination account rolename by which this replication accesses are provided
    '''

    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )
    logging.debug(f"Versioning enabled - Bucket: {bucket_name}")

    s3_client.put_bucket_replication(
        Bucket=bucket_name,
        ReplicationConfiguration={
            'Role': f'{dest_acc_role_name}',
            'Rules': [
                {
                    'Priority': 1,
                    'Filter': {
                        'Prefix': '',
                    },
                    'Destination': {
                        'Bucket': f'arn:aws:s3:::{replica_bucket_name}',
                        'StorageClass': 'STANDARD_IA',
                    },
                    'Status': 'Enabled',
                    'DeleteMarkerReplication': {'Status': 'Enabled'},
                    'ExistingObjectReplication': {
                        'Status': 'Enabled',
                    }, 
                },
            ],
        },
    )
    logging.debug(f"Replication Configuration Done - Bucket: {bucket_name}")


def get_replication_enabled_buckets_by_tag(s3, response, replication_tag_name):
    dr_enabled_buckets = []
    ## List buckets which are enabled for dr-replication through tag: DrReplication = "Enabled"
    logging.info(
        "Getting List of buckets which are enabled for dr-replication through tag: DrReplication = \"Enabled\"")
    for bucket in response['Buckets']:
        logging.info(f"Bucket Name: {bucket}")
        try:
            tagging_response = s3.get_bucket_tagging(
                Bucket=bucket["Name"],
            )

            for tags_dict in tagging_response["TagSet"]:
                print(tags_dict)

                # if "dr_bucket_repliation" in tags_dict.keys():
                if replication_tag_name in tags_dict.values():
                    logging.debug("Value for" + replication_tag_name + "is" + tags_dict["Value"])
                    # if tags_dict["Value"].casefold() == "enabled".casefold():
                    dr_enabled_buckets.append(bucket["Name"])
                else:
                    continue
        except:
            continue
    return dr_enabled_buckets

def testing_buckets():
    ## Testing data - used while debugging
    dr_enabled_buckets = ["dbrs-dl-bucket-raw", "dbrs-dl-bucket-staging"]
    print("Testing buckets as dr_enabled buckets")
    return dr_enabled_buckets

@decorators.victorops_incident_monitor(routing_key=routing_key, job_name='s3_replication_dbrsdpp_to_mstar',
                                       suppress_alerts=suppress_alerts)
def main():
    now = datetime.now()
    formatted_datetime = now.strftime("%d-%m-%Y_%H-%M-%S")
    logfile_name = "bucketReplication-" + formatted_datetime + ".log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.basicConfig(filename=logfile_name, level=logging.INFO)
    logging.info(f'Execution Started at {formatted_datetime}')

    role_name = os.environ["role_name_account2"]
    role_name_account1 = os.environ["role_name_account1"]
    replication_tag_name = os.environ["replication_tag_name"]
    dr_buckets_region = os.environ["dr_buckets_region"]
    
    print("role_name_account2:"+ role_name_account2)
    print("role_name_account2:" + role_name_account1)
    print("role_name_account2:" + replication_tag_name)
    print("role_name_account2:" + dr_buckets_region)

    logging.debug(f'Account2 Role: {role_name_account2} \n Account1 Role: {role_name_account1} \n'
                  f'Replication Tag Name {replication_tag_name} \n  DR Region: {dr_buckets_region} \n')

    logging.info("Getting current branches available in CR aws account")
    ## Through boto s3 api find current list of buckets in aws account
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    list_of_current_buckets = []
    for bucket in response['Buckets']:
        logging.debug(f"Bucket Name {bucket}")
        list_of_current_buckets.append(bucket["Name"])

    count = len(list_of_current_buckets)
    logging.info(f'Existing CR buckets count:\n {count}')
    logging.info(f'Existing CR buckets:\n {list_of_current_buckets}')

    os.environ["AWS_ACCESS_KEY_ID"] = os.environ["USER_AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["USER_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"] = os.environ["USER_AWS_DEFAULT_REGION"]

    ## Connect to Account1 and get list of buckets having tag
    s3_client_on_source = boto3.client(
        's3',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    response = s3_client_on_source.list_buckets()

    dr_enabled_buckets = get_replication_enabled_buckets_by_tag(s3_client_on_source, response, replication_tag_name)

    ## Testing data - uncomment while debugging
    #dr_enabled_buckets = testing_buckets()

    ## List of all the buckets having tag: DrReplication = "Enabled"
    count = len(dr_enabled_buckets)
    logging.info(f"Count all buckets with tag DrReplication = \"Enabled\": \n {count}")
    logging.info(f"List of all buckets with tag DrReplication = \"Enabled\": \n {dr_enabled_buckets} ")

    '''
    Loop Description: 
    For each bucket that needs replication
        Check if bucket exists in account2 if no create one
        if yes, just put the replication configuration
        and also put replication configuration on account1 bucket for bi-directional sync
    '''

    logging.info("Creating bucket or applying replication configuration if present")
    for bucketname in dr_enabled_buckets:
        dr_bucketname = 'dr-' + bucketname
        logging.debug(f"Bucket Name: {bucketname}, DR Bucket Name: {dr_bucketname}")
        if not ((check_if_bucket_exist(dr_bucketname, list_of_current_buckets))):
            logging.info("Creating DR Bucket")
            create_dr_bucket(s3, bucketname, dr_bucketname, dr_buckets_region, role_name_account2, list_of_current_buckets)

        else:
            logging.info(f"Adding bucket policy for bucket: {dr_bucketname}")
            add_bucket_policy(s3, dr_bucketname, role_name_account1)
            logging.info(f"Putting replication configuration as {dr_bucketname} to {bucketname}")
            put_replication_configuration(s3, dr_bucketname, bucketname, role_name_account2)

        logging.info(f"Putting replication configuration as {bucketname} to {dr_bucketname}")
        put_replication_configuration(s3_client_on_source, bucketname, dr_bucketname, role_name_account1)

    now = datetime.now()
    formatted_datetime = now.strftime("%d-%m-%Y_%H-%M-%S")
    logging.info(f'Execution ended at {formatted_datetime}')

if __name__ == "__main__":
    main()