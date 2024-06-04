import boto3
import json

# Load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Initialize the S3 client with values from the config
s3_client = boto3.client('s3', 
                         aws_access_key_id=config['aws_access_key_id'],
                         aws_secret_access_key=config['aws_secret_access_key'],
                         region_name=config['region_name'])

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    target_bucket = config['target_bucket_copy']
    copy_source = {'Bucket': source_bucket, 'Key': object_key}
   
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    s3_client.copy_object(Bucket=target_bucket, Key=object_key, CopySource=copy_source)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Copy completed successfully')
    }
