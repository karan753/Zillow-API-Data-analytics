# Zillow API Data analytics

This project contains Lambda functions and an Airflow DAG for processing Zillow data. The Lambda functions copy raw JSON files from one S3 bucket to another and transform them into CSV format. The Airflow DAG extracts Zillow data, uploads it to S3, and then transfers it to Redshift.

## Project Structure

- `CopyrawJson.py`: Copies raw JSON files from one S3 bucket to another.
- `Transformation.py`: Transforms JSON files to CSV format and uploads them to S3.
- `zillow_airflow_dag.py`: Airflow DAG for extracting Zillow data, uploading to S3, and transferring to Redshift.
- `config.json`: Configuration file for storing AWS credentials and other sensitive information.

## Getting Started

### Prerequisites

- Python 3.x
- AWS CLI
- Airflow
- Boto3
- Pandas

## Set up a virtual environment and install dependencies:

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt 

Create the `config.json` file:

{
    "aws_access_key_id": "XXXXXX",
    "aws_secret_access_key": "XXXXXX",
    "region_name": "XXXXXX",
    "target_bucket_copy": "XXXXXX",
    "target_bucket_csv": "XXXXXX",
    "api_host_key": {
        "x-rapidapi-key": "XXXXXX",
        "x-rapidapi-host": "XXXXXX"
    },
    "s3_bucket": "XXXXXX"
}

