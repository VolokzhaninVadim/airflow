
# For work with datetime
import pendulum
# For work with airflow
from airflow import DAG
from airflow.operators.python import PythonOperator


def update_duckdns() -> None:
    '''
    Update IP on https://www.duckdns.org/
    '''
    # For update ip on duckdns
    from src.duckdns_update import DuckDnsUpdater
    duckdns_updater = DuckDnsUpdater()
    duckdns_updater.update_duckdns()


args = {
    'retries': 2,
    'owner': 'Volokzhanin Vadim'
}

with DAG(
    dag_id='update_dns',
    schedule='@hourly',
    start_date=pendulum.datetime(2023, 2, 12, tz="Europe/Moscow"),
    description='Обновления IP на https://www.duckdns.org/',
    catchup=False,
    default_args=args
) as dag:
    update_duckdns = PythonOperator(
        task_id="update_duckdns",
        python_callable=update_duckdns
    )
