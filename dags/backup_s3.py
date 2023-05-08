# Work with OS
import os
# For work with datetime
import pendulum
# For work with airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

PASSWORD_ARCHIVE_BACKUP_DOCKER = os.environ.get('PASSWORD_ARCHIVE_BACKUP_DOCKER')
S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
S3_AWS_ACCESS_KEY_ID = os.environ.get('S3_AWS_ACCESS_KEY_ID')
S3_AWS_SECRET_ACCESS_KEY = os.environ.get('S3_AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET')

s3_args_dict = {
    'endpoint_url': S3_ENDPOINT_URL,
    'aws_access_key_id': S3_AWS_ACCESS_KEY_ID,
    'aws_secret_access_key': S3_AWS_SECRET_ACCESS_KEY,
    'bucket': S3_BUCKET
}


def update_s3() -> None:
    '''
    Update IP on https://www.duckdns.org/
    '''
    # For update ip on duckdns
    from src.backup_s3 import Backup
    backup = Backup(**s3_args_dict)
    backup.update_s3()


args = {
    'retries': 3,
    'owner': 'Volokzhanin Vadim'
}

with DAG(
    dag_id='update_s3',
    schedule='@hourly',
    start_date=pendulum.datetime(2023, 2, 12, tz='Europe/Moscow'),
    description='Обновлениу backup сервера',
    catchup=False,
    default_args=args
) as dag:
    update_duckdns = PythonOperator(
        task_id='update_s3',
        python_callable=update_s3
    )
