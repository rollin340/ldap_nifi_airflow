from airflow import DAG
from airflow.operators.dummy import DummyOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2022, 1, 1)
}

with DAG('test_dag_2', tags=['company_2'], schedule_interval='@daily', 
    default_args=default_args, catchup=False) as dag:

    task_a = DummyOperator(
        task_id="task_a"
    )