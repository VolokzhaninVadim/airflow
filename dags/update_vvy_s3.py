# Work with OS
import os
# For work with datetime
import pendulum
# For work with airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

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
    dag_id='update_vvy_s3',
    schedule='@daily',
    start_date=pendulum.datetime(2023, 5, 13, tz='Europe/Moscow'),
    description='Делаем backup сервера (медиа и документы)',
    catchup=False,
    default_args=args
    ) as dag:

    wait_update_docker_s3 = ExternalTaskSensor(
        task_id='wait_update_docker_s3',
        external_dag_id='update_docker_s3',
        external_task_id='update_private_library',
        start_date=pendulum.datetime(2023, 5, 13, tz='Europe/Moscow'),
        timeout=50,
    )

    update_document = PythonOperator(
        provide_context=True,
        task_id='update_document',
        python_callable=update_s3,
        op_kwargs={'path': 'document'}
    )

    wait_update_docker_s3 >> update_document




