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

def update_s3(path: str) -> None:
    '''
    Update files in s3 for dns.

    Parameters
    ----------
    path : str
        Path for update data in S3.
    '''
    # For update ip on duckdns
    from src.backup_s3 import Backup
    backup = Backup(**s3_args_dict)
    backup.update_s3(dict_path=path)


args = {
    'retries': 3,
    'owner': 'Volokzhanin Vadim'
}

with DAG(
    dag_id='update_docker_s3',
    schedule='@daily',
    start_date=pendulum.datetime(2023, 5, 13, tz='Europe/Moscow'),
    description='Делаем backup сервера (docker)',
    catchup=False,
    default_args=args
    ) as dag:


    update_airflow = PythonOperator(
        provide_context=True,
        task_id='update_airflow',
        python_callable=update_s3,
        op_kwargs={'path': 'airflow'}
    )

    update_dns = PythonOperator(
        provide_context=True,
        task_id='update_dns',
        python_callable=update_s3,
        op_kwargs={'path': 'dns'}
    )

    update_jupyterlab = PythonOperator(
        provide_context=True,
        task_id='update_jupyterlab',
        python_callable=update_s3,
        op_kwargs={'path': 'jupyterlab'}
    )

    update_private_cloud = PythonOperator(
        provide_context=True,
        task_id='update_private_cloud',
        python_callable=update_s3,
        op_kwargs={'path': 'private_cloud'}
    )

    update_media_serve = PythonOperator(
        provide_context=True,
        task_id='update_media_serve',
        python_callable=update_s3,
        op_kwargs={'path': 'private_media_server'}
    )

    update_private_library = PythonOperator(
        provide_context=True,
        task_id='update_private_library',
        python_callable=update_s3,
        op_kwargs={'path': 'private_library'}
    )

    [update_dns, update_jupyterlab, update_airflow] >> update_private_cloud >> update_media_serve >> update_private_library
