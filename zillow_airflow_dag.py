from airflow import DAG
from datetime import timedelta, datetime
import json
import requests
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator


with open('/home/ubuntu/airflow/config.json', 'r') as config_file:
    config = json.load(config_file)

api_host_key = config['api_host_key']
s3_bucket = config['s3_bucket']
now = datetime.now()
dt_now_string = now.strftime("%d%m%Y%H%M%S")

def extract_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']
    
    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()
    
    output_file_path = f"/home/ubuntu/response_data_{dt_string}.json"
    file_str = f'response_data_{dt_string}.csv'

    with open(output_file_path, "w") as output_file:
        json.dump(response_data, output_file, indent=4)
    return [output_file_path, file_str]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'email': ['myemail@domain.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15)
}

with DAG('zillow_analytics_dag',
        default_args=default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:

    extract_zillow_data_var = PythonOperator(
        task_id='tsk_extract_zillow_data_var',
        python_callable=extract_zillow_data,
        op_kwargs={
            'url': 'https://zillow56.p.rapidapi.com/search',
            'querystring': {"location":"houston, tx"},
            'headers': api_host_key,
            'date_string': dt_now_string
        }
    )

    load_to_s3 = BashOperator(
        task_id='tsk_load_to_s3',
        bash_command='aws s3 mv {{ ti.xcom_pull("tsk_extract_zillow_data_var")[0] }} s3://endtoendyoutube-ym-bucket/',
    )

    is_file_in_s3_available = S3KeySensor(
        task_id='tsk_is_file_in_s3_available',
        bucket_key='{{ ti.xcom_pull("tsk_extract_zillow_data_var")[1] }}',
        bucket_name=s3_bucket,
        aws_conn_id='aws_s3_conn',
        wildcard_match=False,
        timeout=60,
        poke_interval=5,
    )

    transfer_s3_to_redshift = S3ToRedshiftOperator(
        task_id='tsk_transfer_s3_to_redshift',
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket=s3_bucket,
        s3_key='{{ ti.xcom_pull("tsk_extract_zillow_data_var")[1] }}',
        schema='PUBLIC',
        table='zillowdata',
        copy_options=["csv IGNOREHEADER 1"],
    )

    extract_zillow_data_var >> load_to_s3 >> is_file_in_s3_available >> transfer_s3_to_redshift
