import boto3
import json
import pandas as pd


with open('config.json', 'r') as config_file:
    config = json.load(config_file)


s3_client = boto3.client('s3', 
                         aws_access_key_id=config['aws_access_key_id'],
                         aws_secret_access_key=config['aws_secret_access_key'],
                         region_name=config['region_name'])

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    target_bucket = config['target_bucket_csv']
    target_file_name = object_key[:-5]
   
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    
    response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
    data = response['Body'].read().decode('utf-8')
    data = json.loads(data)
    
    f = [i for i in data["results"]]
    df = pd.DataFrame(f)
    

    selected_columns = ['bathrooms', 'bedrooms', 'city', 'homeStatus', 
                        'homeType', 'livingArea', 'price', 'rentZestimate', 'zipcode']
    df = df[selected_columns]
    

    csv_data = df.to_csv(index=False)
    

    s3_client.put_object(Bucket=target_bucket, Key=f"{target_file_name}.csv", Body=csv_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV conversion and S3 upload completed successfully')
    }
